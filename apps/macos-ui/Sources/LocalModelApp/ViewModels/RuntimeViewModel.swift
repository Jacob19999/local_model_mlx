import Foundation

struct RuntimeModel: Decodable {
    let id: String
    let runtime: String
    let turboquant_compatible: Bool

    var runtimeLabel: String {
        turboquant_compatible ? "\(runtime) + turbo" : runtime
    }
}

struct ModelsResponse: Decodable {
    let data: [RuntimeModel]
}

@MainActor
final class RuntimeViewModel: ObservableObject {
    @Published var models: [RuntimeModel] = []
    @Published var selectedModelID: String?
    @Published var statusLine = "Waiting for local API"
    @Published var activeRuntime = "unknown"

    let apiBaseURL: URL

    init() {
        if let value = ProcessInfo.processInfo.environment["LOCAL_MODEL_API_BASE_URL"],
           let url = URL(string: value) {
            apiBaseURL = url
        } else {
            apiBaseURL = URL(string: "http://127.0.0.1:8000")!
        }
    }

    func refresh() async {
        do {
            let url = apiBaseURL.appending(path: "/v1/models")
            let (data, _) = try await URLSession.shared.data(from: url)
            let response = try JSONDecoder().decode(ModelsResponse.self, from: data)
            models = response.data
            selectedModelID = selectedModelID ?? models.first?.id
            activeRuntime = models.first?.runtime ?? "mlx"
            statusLine = models.isEmpty ? "No registered models" : "Connected to local API"
        } catch {
            models = []
            activeRuntime = "unavailable"
            statusLine = "API unavailable: \(error.localizedDescription)"
        }
    }
}

