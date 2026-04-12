// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "LocalModelApp",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "LocalModelApp", targets: ["LocalModelApp"])
    ],
    targets: [
        .executableTarget(
            name: "LocalModelApp",
            path: "Sources/LocalModelApp"
        )
    ]
)

