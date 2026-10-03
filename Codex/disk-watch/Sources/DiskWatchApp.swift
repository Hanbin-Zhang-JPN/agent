import SwiftUI

@MainActor final class Monitor: ObservableObject {
    @Published var drives: [DriveSample] = []
    @Published var selectedID = ""
    @Published var readRate = 0.0
    @Published var writeRate = 0.0
    @Published var sessionRead: UInt64 = 0
    @Published var sessionWritten: UInt64 = 0
    @Published var smart = SmartSample(message: "正在读取…")
    @Published var history: [(Double, Double)] = []
    @Published var updatedAt = Date()

    private var previous: DriveSample?
    private var previousAt: Date?
    private var smartAt = Date.distantPast
    private var timer: Timer?

    var selected: DriveSample? { drives.first { $0.id == selectedID } }

    init() {
        refresh()
        timer = Timer.scheduledTimer(withTimeInterval: 2, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.refresh() }
        }
    }

    func choose(_ id: String) {
        guard id != selectedID else { return }
        selectedID = id
        previous = nil
        previousAt = nil
        sessionRead = 0
        sessionWritten = 0
        readRate = 0
        writeRate = 0
        history = []
        smart = SmartSample(message: "正在读取…")
        smartAt = .distantPast
        refresh()
    }

    func refresh() {
        let now = Date()
        drives = DiskProbe.samples()
        if selectedID.isEmpty || !drives.contains(where: { $0.id == selectedID }) {
            selectedID = drives.first?.id ?? ""
            previous = nil
            previousAt = nil
        }
        guard let current = selected else { return }
        if let old = previous, let oldAt = previousAt,
           old.id == current.id,
           current.readBytes >= old.readBytes,
           current.writtenBytes >= old.writtenBytes {
            let seconds = max(now.timeIntervalSince(oldAt), 0.001)
            let readDelta = current.readBytes - old.readBytes
            let writeDelta = current.writtenBytes - old.writtenBytes
            readRate = Double(readDelta) / seconds
            writeRate = Double(writeDelta) / seconds
            sessionRead &+= readDelta
            sessionWritten &+= writeDelta
            history.append((readRate, writeRate))
            if history.count > 60 { history.removeFirst() }
        } else {
            readRate = 0
            writeRate = 0
        }
        previous = current
        previousAt = now
        updatedAt = now
        if now.timeIntervalSince(smartAt) >= 60 {
            smartAt = now
            smart = SmartProbe.read(disk: current.id)
        }
    }
}

private func bytes(_ value: UInt64) -> String { ByteCountFormatter.string(fromByteCount: Int64(clamping: value), countStyle: .decimal) }
private func rate(_ value: Double) -> String { bytes(UInt64(max(0, value))) + "/s" }

struct ValueCard: View {
    let title: String
    let value: String
    let caption: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 9) {
            Text(title).font(.system(size: 13, weight: .medium)).foregroundStyle(.secondary)
            Text(value).font(.system(size: 25, weight: .semibold, design: .rounded)).monospacedDigit().foregroundStyle(color)
            Text(caption).font(.system(size: 11)).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(17)
        .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 16))
    }
}

struct ActivityBars: View {
    let history: [(Double, Double)]
    private let readColor = Color(red: 0.30, green: 0.60, blue: 0.97)
    private let writeColor = Color(red: 0.98, green: 0.62, blue: 0.32)

    var body: some View {
        GeometryReader { geometry in
            let maxValue = max(history.map { max($0.0, $0.1) }.max() ?? 1, 1)
            HStack(alignment: .bottom, spacing: 2) {
                ForEach(0..<60, id: \.self) { index in
                    let sample = index < 60 - history.count ? (0.0, 0.0) : history[index - (60 - history.count)]
                    VStack(spacing: 2) {
                        RoundedRectangle(cornerRadius: 2).fill(readColor)
                            .frame(height: max(2, geometry.size.height * sample.0 / maxValue))
                        RoundedRectangle(cornerRadius: 2).fill(writeColor)
                            .frame(height: max(2, geometry.size.height * sample.1 / maxValue))
                    }
                    .frame(maxWidth: .infinity, alignment: .bottom)
                }
            }
        }
    }
}

struct ContentView: View {
    @ObservedObject var monitor: Monitor
    private let readColor = Color(red: 0.30, green: 0.60, blue: 0.97)
    private let writeColor = Color(red: 0.98, green: 0.62, blue: 0.32)

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text("磁盘观察").font(.system(size: 30, weight: .bold, design: .rounded))
                        Text("物理磁盘读写与 SSD 寿命").foregroundStyle(.secondary)
                    }
                    Spacer()
                    Text("每 2 秒更新").font(.caption).foregroundStyle(.secondary).padding(.top, 9)
                }

                if monitor.drives.isEmpty {
                    ContentUnavailableView("未找到物理磁盘", systemImage: "externaldrive.badge.questionmark", description: Text("无法从 IOKit 读取磁盘统计数据。"))
                } else {
                    Picker("磁盘", selection: Binding(get: { monitor.selectedID }, set: { monitor.choose($0) })) {
                        ForEach(monitor.drives) { drive in
                            Text("\(drive.name) · \(drive.id) · \(bytes(drive.size))").tag(drive.id)
                        }
                    }

                    HStack(spacing: 12) {
                        ValueCard(title: "实时读取", value: rate(monitor.readRate), caption: "物理磁盘吞吐量", color: readColor)
                        ValueCard(title: "实时写入", value: rate(monitor.writeRate), caption: "物理磁盘吞吐量", color: writeColor)
                    }

                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("最近 2 分钟").font(.headline)
                            Spacer()
                            Circle().fill(readColor).frame(width: 8, height: 8)
                            Text("读取").font(.caption).foregroundStyle(.secondary)
                            Circle().fill(writeColor).frame(width: 8, height: 8)
                            Text("写入").font(.caption).foregroundStyle(.secondary)
                        }
                        ActivityBars(history: monitor.history).frame(height: 92)
                    }
                    .padding(17)
                    .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 16))

                    HStack(spacing: 12) {
                        ValueCard(title: "本次开机读取", value: bytes(monitor.selected?.readBytes ?? 0), caption: "IOKit 计数器，重启后归零", color: .primary)
                        ValueCard(title: "本次开机写入", value: bytes(monitor.selected?.writtenBytes ?? 0), caption: "IOKit 计数器，重启后归零", color: .primary)
                    }
                    HStack(spacing: 12) {
                        ValueCard(title: "监控期间读取", value: bytes(monitor.sessionRead), caption: "从打开本程序起", color: .primary)
                        ValueCard(title: "监控期间写入", value: bytes(monitor.sessionWritten), caption: "从打开本程序起", color: .primary)
                    }

                    VStack(alignment: .leading, spacing: 13) {
                        HStack {
                            Text("SSD 磨损与终身总量").font(.headline)
                            Spacer()
                            Button("刷新 SMART") { monitor.smart = SmartProbe.read(disk: monitor.selectedID) }
                                .buttonStyle(.borderless)
                        }
                        Text(monitor.smart.message).font(.caption).foregroundStyle(.secondary)
                        Divider()
                        HStack(spacing: 12) {
                            smartValue("已用寿命", monitor.smart.percentageUsed.map { "\($0)%" }, "NVMe 估计值")
                            smartValue("终身读取", monitor.smart.lifetimeReadBytes.map(bytes), "设备 SMART 计数")
                            smartValue("终身写入", monitor.smart.lifetimeWrittenBytes.map(bytes), "设备 SMART 计数")
                        }
                        Text("磨损百分比由 SSD 固件估算；不同设备可能不提供。读写计数不等于 NAND 实际擦写量。")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    .padding(17)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color(nsColor: .controlBackgroundColor), in: RoundedRectangle(cornerRadius: 16))
                }
                Text("数据保留在本机；程序不会上传磁盘信息。")
                    .font(.caption2).foregroundStyle(.tertiary)
            }
            .padding(24)
        }
        .frame(minWidth: 650, minHeight: 660)
        .background(Color(nsColor: .windowBackgroundColor))
    }

    private func smartValue(_ title: String, _ value: String?, _ caption: String) -> some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(title).font(.caption).foregroundStyle(.secondary)
            Text(value ?? "不可用").font(.system(size: 21, weight: .semibold, design: .rounded)).monospacedDigit()
            Text(caption).font(.caption2).foregroundStyle(.tertiary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

@main struct DiskWatchApp: App {
    @StateObject private var monitor = Monitor()

    var body: some Scene {
        WindowGroup("磁盘观察") { ContentView(monitor: monitor) }
            .windowResizability(.contentMinSize)
        MenuBarExtra("磁盘观察", systemImage: "internaldrive") {
            if let disk = monitor.selected {
                Text("\(disk.name) · \(disk.id)")
                Text("读取 \(rate(monitor.readRate))  ·  写入 \(rate(monitor.writeRate))")
                Text("开机写入 \(bytes(disk.writtenBytes))")
            } else {
                Text("未找到磁盘")
            }
            Divider()
            Button("退出磁盘观察") { NSApplication.shared.terminate(nil) }
        }
    }
}
