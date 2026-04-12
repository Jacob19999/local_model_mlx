import SwiftUI

@main
struct LocalModelApp: App {
    @StateObject private var viewModel = RuntimeViewModel()

    var body: some Scene {
        WindowGroup {
            NavigationSplitView {
                List(viewModel.models, id: \.id, selection: $viewModel.selectedModelID) { model in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(model.id)
                            .font(.headline)
                        Text(model.runtimeLabel)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                .navigationTitle("Models")
                .toolbar {
                    Button("Refresh") {
                        Task { await viewModel.refresh() }
                    }
                }
            } detail: {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Local Model Runtime")
                        .font(.largeTitle)
                    Text(viewModel.statusLine)
                        .foregroundStyle(.secondary)
                    Text("Selected model: \(viewModel.selectedModelID ?? "None")")
                    Text("Active runtime: \(viewModel.activeRuntime)")
                    Text("API base URL: \(viewModel.apiBaseURL.absoluteString)")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    Spacer()
                }
                .padding(24)
            }
            .task {
                await viewModel.refresh()
            }
        }
    }
}

