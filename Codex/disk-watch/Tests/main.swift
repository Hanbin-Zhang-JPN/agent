import Foundation

let drives = DiskProbe.samples()
guard !drives.isEmpty else {
    fputs("No physical disk statistics available\n", stderr)
    exit(1)
}
for drive in drives {
    print("\(drive.id) \(drive.name): read=\(drive.readBytes) write=\(drive.writtenBytes) size=\(drive.size)")
    precondition(drive.readBytes > 0 && drive.writtenBytes > 0 && drive.size > 0)
}
let smart = SmartProbe.read(disk: drives[0].id)
print("SMART: \(smart.message); wear=\(smart.percentageUsed.map(String.init) ?? "unavailable")")
