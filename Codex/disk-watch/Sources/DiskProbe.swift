import Foundation
import IOKit

struct DriveSample: Identifiable {
    let id: String
    let name: String
    let size: UInt64
    let readBytes: UInt64
    let writtenBytes: UInt64
    let readOperations: UInt64
    let writeOperations: UInt64
}

enum DiskProbe {
    static func samples() -> [DriveSample] {
        guard let matching = IOServiceMatching("IOBlockStorageDriver") else { return [] }
        var iterator: io_iterator_t = 0
        guard IOServiceGetMatchingServices(kIOMainPortDefault, matching, &iterator) == KERN_SUCCESS else { return [] }
        defer { IOObjectRelease(iterator) }

        var result: [DriveSample] = []
        while case let driver = IOIteratorNext(iterator), driver != 0 {
            defer { IOObjectRelease(driver) }
            guard let stats = property(driver, "Statistics") as? [String: Any],
                  let read = uint(stats["Bytes (Read)"]),
                  let written = uint(stats["Bytes (Write)"]) else { continue }

            var childIterator: io_iterator_t = 0
            guard IORegistryEntryGetChildIterator(driver, kIOServicePlane, &childIterator) == KERN_SUCCESS else { continue }
            defer { IOObjectRelease(childIterator) }
            while case let child = IOIteratorNext(childIterator), child != 0 {
                defer { IOObjectRelease(child) }
                guard let whole = property(child, "Whole") as? Bool, whole,
                      let bsdName = property(child, "BSD Name") as? String,
                      let name = registryName(child) else { continue }
                let size = uint(property(child, "Size")) ?? 0
                result.append(DriveSample(
                    id: bsdName, name: name.replacingOccurrences(of: " Media", with: ""),
                    size: size, readBytes: read, writtenBytes: written,
                    readOperations: uint(stats["Operations (Read)"]) ?? 0,
                    writeOperations: uint(stats["Operations (Write)"]) ?? 0
                ))
            }
        }
        return result.sorted { $0.id.localizedStandardCompare($1.id) == .orderedAscending }
    }

    private static func property(_ entry: io_registry_entry_t, _ key: String) -> Any? {
        IORegistryEntryCreateCFProperty(entry, key as CFString, kCFAllocatorDefault, 0)?.takeRetainedValue()
    }

    private static func registryName(_ entry: io_registry_entry_t) -> String? {
        var name = [CChar](repeating: 0, count: 128)
        guard IORegistryEntryGetName(entry, &name) == KERN_SUCCESS else { return nil }
        return String(cString: name)
    }

    private static func uint(_ value: Any?) -> UInt64? {
        guard let number = value as? NSNumber else { return nil }
        return number.uint64Value
    }
}

struct SmartSample {
    var percentageUsed: Int?
    var lifetimeReadBytes: UInt64?
    var lifetimeWrittenBytes: UInt64?
    var availableSpare: Int?
    var message: String
}

enum SmartProbe {
    static func read(disk: String) -> SmartSample {
        guard let executable = ["/opt/homebrew/sbin/smartctl", "/opt/homebrew/bin/smartctl", "/usr/local/sbin/smartctl", "/usr/local/bin/smartctl"].first(where: FileManager.default.isExecutableFile(atPath:)) else {
            return SmartSample(message: "未安装 smartmontools；可用 brew install smartmontools 安装")
        }
        guard let json = run(executable, ["-a", "-j", "/dev/\(disk)"]),
              let log = json["nvme_smart_health_information_log"] as? [String: Any] else {
            return SmartSample(message: "此磁盘的 SMART 数据不可读取（设备、系统或权限限制）")
        }
        return SmartSample(
            percentageUsed: int(log["percentage_used"]),
            lifetimeReadBytes: dataUnits(log["data_units_read"]),
            lifetimeWrittenBytes: dataUnits(log["data_units_written"]),
            availableSpare: int(log["available_spare"]),
            message: "NVMe SMART 设备报告值"
        )
    }

    private static func run(_ executable: String, _ args: [String]) -> [String: Any]? {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: executable)
        process.arguments = args
        let output = Pipe()
        process.standardOutput = output
        process.standardError = Pipe()
        do { try process.run() } catch { return nil }
        let data = output.fileHandleForReading.readDataToEndOfFile()
        process.waitUntilExit()
        return (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
    }

    private static func int(_ value: Any?) -> Int? {
        (value as? NSNumber)?.intValue
    }

    private static func dataUnits(_ value: Any?) -> UInt64? {
        // NVMe SMART units are 1000 × 512 bytes. Large 128-bit counters are left unavailable.
        let units: UInt64?
        if let n = value as? NSNumber { units = n.uint64Value }
        else if let s = value as? String { units = UInt64(s.replacingOccurrences(of: ",", with: "")) }
        else { units = nil }
        guard let units, units <= UInt64.max / 512_000 else { return nil }
        return units * 512_000
    }
}
