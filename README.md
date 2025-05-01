# tofuref

A terminal application to browse OpenTofu provider documentation from the terminal.

![Screenshot](https://github.com/djetelina/tofuref/blob/main/screenshots/welcome.png?raw=true)

## Installation

```bash
pipx install tofuref
```

## Usage

Run the application:

```bash
tofuref
```

## Development

### Provider Data Fetching

tofuref uses git cloning to fetch provider data from the OpenTofu registry and provider repositories:

1. **Provider List**: On startup, tofuref fetches the list of available providers
   from the [OpenTofu Registry](https://github.com/opentofu/registry/tree/main/providers).

2. **Provider Documentation**: When a provider is selected in the UI, tofuref fetches
   documentation from the provider's GitHub repository. This is done lazily (on-demand).

3. **Persistent Storage**: The application stores cloned repositories in the user's application data directory to avoid
   re-cloning repositories on every startup.

## License

MIT
