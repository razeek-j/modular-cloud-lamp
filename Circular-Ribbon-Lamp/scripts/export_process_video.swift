// Native conversion and media verification. No microphone or system audio is recorded.
import Foundation
import AVFoundation
import AppKit

let arguments = CommandLine.arguments
guard arguments.count == 4 else {
    fatalError("Usage: swift export_process_video.swift input.mov output.mp4 stills-folder")
}
let source = URL(fileURLWithPath: arguments[1])
let destination = URL(fileURLWithPath: arguments[2])
let stills = URL(fileURLWithPath: arguments[3], isDirectory: true)
Task {
    do {
        let asset = AVURLAsset(url: source)
        let duration = try await asset.load(.duration).seconds
        let tracks = try await asset.loadTracks(withMediaType: .video)
        guard let track = tracks.first else { fatalError("No video track") }
        let size = try await track.load(.naturalSize)
        guard let session = AVAssetExportSession(asset: asset, presetName: AVAssetExportPreset1920x1080) else {
            fatalError("Cannot create exporter")
        }
        session.shouldOptimizeForNetworkUse = true
        try await session.export(to: destination, as: .mp4)
        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.maximumSize = CGSize(width: 1280, height: 800)
        try FileManager.default.createDirectory(at: stills, withIntermediateDirectories: true)
        for second in [8.0, 15.0, 23.0, 38.0, 49.0] where second < duration {
            let frame = try await generator.image(at: CMTime(seconds: second, preferredTimescale: 600))
            let rep = NSBitmapImageRep(cgImage: frame.image)
            guard let png = rep.representation(using: .png, properties: [:]) else { continue }
            try png.write(to: stills.appendingPathComponent("01-build-\(Int(second))s.png"))
        }
        let output = AVURLAsset(url: destination)
        let outDuration = try await output.load(.duration).seconds
        print("Verified source: \(duration)s, \(size.width) × \(size.height)")
        print("Verified MP4: \(outDuration)s, \(destination.path)")
        exit(0)
    } catch {
        print("Video export failed: \(error)")
        exit(1)
    }
}
dispatchMain()
