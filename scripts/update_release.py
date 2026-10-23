from pathlib import Path
root = Path(__file__).resolve().parents[1]
files = [root/'index.html', root/'handbook.html', root/'README.md']
replacements = {
 'The ISO filename is <code>IULinux-0.1-alpha1-amd64.iso</code> and its recorded size is 2,952,669,184 bytes. Release artifacts are stored in Cloudflare R2, but the public download endpoint has not been finalized. The release page will be updated when that URL is ready.': 'Download <a href="https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso">IULinux-0.1-alpha1-amd64.iso</a> from the official release host. It is 2,952,669,184 bytes. The matching <a href="https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso.sha256">SHA-256 file</a> is published beside it.',
 'It is stored in Cloudflare R2 bucket <code>iulinux-releases</code>; its public URL is not configured, so this site intentionally has no download button.': 'It is publicly available at <a href="https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso">the official ISO endpoint</a>. The matching checksum file is available at <a href="https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso.sha256">the official SHA-256 endpoint</a>.',
 'sha256sum --check IULinux-0.1-alpha1-amd64.iso.sha256&#10;sha256sum IULinux-0.1-alpha1-amd64.iso': 'curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso&#10;curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso.sha256&#10;sha256sum --check IULinux-0.1-alpha1-amd64.iso.sha256&#10;sha256sum IULinux-0.1-alpha1-amd64.iso',
 'When the official URL and digest are published, verify with:': 'Verify the downloaded artifact before writing installation media:',
 '<a class="text-link text-link-light" href="handbook.html#downloads">Read verification instructions ↗</a>': '<a class="button button-primary" href="https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso">Download ISO ↘</a><a class="text-link text-link-light" href="handbook.html#downloads">Verify SHA-256 ↗</a>',
 'The ISO is built and verified, but the public download endpoint has not been finalized.': 'The ISO is built and verified and the public artifact is available. The formal website launch is still pending.',
 'Public URL pending': 'Public artifact available',
 'The checksum value was not present in the inspected reference material and is not guessed here.': 'The expected SHA-256 is 1d84879fb560819e331983a2b8cbac63051ff233a180f4e62bcf9cfe366f9604. The expected ISO size is 2,952,669,184 bytes.',
 'curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso&#10;curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso.sha256&#10;curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso&#10;curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso.sha256': 'curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso&#10;curl -LO https://releases.irfanuruchi.in/IULinux-0.1-alpha1-amd64.iso.sha256',
 'Public ISO URL is not configured.': 'The formal website launch is still pending even though the public ISO artifact is available.',
 'SHA-256 digest was not present in inspected reference material.': '',
 'The website records the artifact name and size but waits for the R2 public endpoint.': 'The public artifact and checksum endpoints are now available; the formal website launch remains pending.',
 'without exposing an unconfigured download URL.': 'with the public ISO and checksum endpoints recorded in the release section.'
}
for path in files:
    text = path.read_text()
    for old, new in replacements.items(): text = text.replace(old, new)
    path.write_text(text)
