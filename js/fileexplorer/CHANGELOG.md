# @gradio/fileexplorer

## 0.2.2-beta.0

### Patch Changes

- Updated dependencies [[`90449fff6`](https://github.com/gradio-app/gradio/commit/90449fff680e8e7f2c8b7d85faaa0039f109fe97)]:
  - @gradio/atoms@0.2.0-beta.0
  - @gradio/checkbox@0.2.3-beta.0
  - @gradio/file@0.2.2-beta.0
  - @gradio/statustracker@0.2.3-beta.0
  - @gradio/upload@0.3.3-beta.0

## 0.2.1

### Patch Changes

- Updated dependencies [[`796145e2c`](https://github.com/gradio-app/gradio/commit/796145e2c48c4087bec17f8ec0be4ceee47170cb)]:
  - @gradio/client@0.5.1
  - @gradio/file@0.2.1

## 0.2.0

### Highlights

#### new `FileExplorer` component ([#5672](https://github.com/gradio-app/gradio/pull/5672) [`e4a307ed6`](https://github.com/gradio-app/gradio/commit/e4a307ed6cde3bbdf4ff2f17655739addeec941e))

Thanks to a new capability that allows components to communicate directly with the server _without_ passing data via the value, we have created a new `FileExplorer` component.

This component allows you to populate the explorer by passing a glob, but only provides the selected file(s) in your prediction function.

Users can then navigate the virtual filesystem and select files which will be accessible in your predict function. This component will allow developers to build more complex spaces, with more flexible input options.

![output](https://github.com/pngwn/MDsveX/assets/12937446/ef108f0b-0e84-4292-9984-9dc66b3e144d)

For more information check the [`FileExplorer` documentation](https://gradio.app/docs/fileexplorer).

Thanks [@aliabid94](https://github.com/aliabid94)!
