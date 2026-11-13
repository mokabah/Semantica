# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Please do not disclose security issues in public issues. Use GitHub's **Report a
vulnerability** option on the repository's Security tab (private vulnerability reporting).
If that option is not available, open an issue that states only that you wish to report a
security matter, without technical details, and a maintainer will arrange a private channel.

Semantica has no runtime dependencies and performs no network access. Relevant issues are
most likely to concern unsafe handling of input size or of output paths in the command-line
interface. Input text is limited to 20,000 characters by default.
