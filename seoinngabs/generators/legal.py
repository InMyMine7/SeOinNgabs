"""Generator dokumen legal: ToS, Privacy Policy, Disclaimer (fix O1-O4).

Perbaikan vs main.py lama:
- Variabel services/third_party_services privacy dipakai di template (fix O1).
- Semua template disclaimer menyertakan kontak email (fix O2).
- Input di-escape (fix O3).
- Import datetime yang tidak terpakai dibuang (fix O4).
"""

import time
from pathlib import Path

from ..core.output import colorize, escape_html


def _confirm_overwrite(path: Path) -> bool:
    if not path.exists():
        return True
    return input(f"{path.name} sudah ada. Timpa? (y/n): ").strip().lower() == "y"


def build_terms_and_conditions(website_name: str, website_url: str, company_name: str, governing_law: str, contact_email: str) -> str:
    """Template Terms and Conditions dengan semua input ter-escape."""
    e = escape_html
    wn, wu, cn, gl, ce = e(website_name), e(website_url), e(company_name), e(governing_law), e(contact_email)
    return f"""<h1>Terms and Conditions for {wn}</h1>

<p>Welcome to <strong>{wn}</strong>! These terms and conditions outline the rules and regulations for the use of <a href="{wu}">{wu}</a>. By accessing this website, we assume you accept these terms and conditions in full. Do not continue to use {wn}'s website if you do not accept all of the terms and conditions stated on this page.</p>

<h2>1. License</h2>
<p>Unless otherwise stated, {cn} and/or its licensors own the intellectual property rights for all material on {wn}. All intellectual property rights are reserved. You may view and/or print pages from {wu} for your personal use subject to restrictions set in these terms and conditions.</p>

<h2>2. You Must Not</h2>
<p>You are specifically restricted from all of the following:</p>
<ul>
    <li>Publishing any material from {wu} in any other media</li>
    <li>Selling, sublicensing, and/or otherwise commercializing any website material</li>
    <li>Using this website in any way that is damaging, or that could be damaging, to this website</li>
    <li>Using this website contrary to applicable laws and regulations</li>
</ul>

<h2>3. Content Liability</h2>
<p>We shall not be held responsible for any content that appears on your website. You agree to protect and defend us against all claims that arise on your website.</p>

<h2>4. Hyperlinking to Our Content</h2>
<p>The following organizations may link to our website without prior written approval:</p>
<ul>
    <li>Government agencies</li>
    <li>Search engines</li>
    <li>News organizations</li>
    <li>Online directory distributors</li>
</ul>

<h2>5. Governing Law</h2>
<p>These terms and conditions will be governed by and interpreted in accordance with the laws of {gl}, and you submit to the jurisdiction of the courts located in {gl} for the resolution of any disputes.</p>

<h2>6. Modifications to Terms</h2>
<p>{cn} reserves the right to revise these terms and conditions at any time. By using this website, you are expected to review these terms regularly.</p>

<h2>Contact Us</h2>
<p>If you have any questions about our Terms and Conditions, please contact us at:</p>
<ul>
    <li>Email: <a href="mailto:{ce}">{ce}</a></li>
</ul>

<p>Last updated: {time.strftime("%Y-%m-%d")}</p>
"""


def build_privacy_policy(website_name: str, website_url: str, company_name: str, company_email: str, services: str = "", third_party_services: str = "") -> str:
    """Template Privacy Policy — layanan user diinterpolasi (fix O1)."""
    e = escape_html
    wn, wu, cn, ce = e(website_name), e(website_url), e(company_name), e(company_email)
    if services:
        service_items = "\n".join(f"    <li>{escape_html(s.strip())}</li>" for s in services.split(",") if s.strip())
        services_html = f"<ul>\n{service_items}\n    </ul>"
    else:
        services_html = "<p>See our website for the services we provide.</p>"
    if third_party_services:
        tp_items = "\n".join(f"    <li>{escape_html(t.strip())}</li>" for t in third_party_services.split(",") if t.strip())
        third_party_html = f"<ul>\n{tp_items}\n    </ul>"
    else:
        third_party_html = "<ul>\n    <li>Google Analytics</li>\n    <li>Facebook Pixel</li>\n    <li>Other third-party services</li>\n    </ul>"
    return f"""<h1>Privacy Policy for {wn}</h1>

<p>At <strong>{wn}</strong> (<a href="{wu}">{wu}</a>), accessible from {wu}, one of our main priorities is the privacy of our visitors. This Privacy Policy document contains types of information that is collected and recorded by {wn} and how we use it.</p>

<h2>1. Information We Collect</h2>
<ul>
    <li>Personal identification information (Name, email address, etc.)</li>
    <li>Non-personal identification information (browser type, device information, etc.)</li>
</ul>

<h2>2. How We Use Your Information</h2>
<p>We use the information we collect to provide and improve our services:</p>
{services_html}

<h2>3. Third-Party Services</h2>
<p>{wn} uses third-party services to enhance the user experience. These services include, but are not limited to:</p>
{third_party_html}

<h2>4. Cookies</h2>
<p>We use cookies to store non-personal information about our visitors. Cookies help us improve user experience by remembering preferences, and tracking website usage.</p>

<h2>5. Data Security</h2>
<p>We take appropriate security measures to protect against unauthorized access, alteration, or destruction of your personal data.</p>

<h2>6. Your Rights</h2>
<ul>
    <li>Access, update, or delete your personal data</li>
    <li>Opt-out of receiving marketing communications at any time</li>
</ul>

<h2>7. Changes to This Privacy Policy</h2>
<p>{wn} reserves the right to update or change our privacy policy at any time. We encourage you to check this page periodically for any updates.</p>

<h2>Contact Us</h2>
<p>If you have any questions about this Privacy Policy, please contact us at:</p>
<ul>
    <li>Email: <a href="mailto:{ce}">{ce}</a></li>
    <li>Website: <a href="{wu}">{wu}</a></li>
</ul>

<p>Last updated: {time.strftime("%Y-%m-%d")}</p>
"""


def build_disclaimer(website_name: str, website_url: str, company_name: str, company_email: str, disclaimer_type: str) -> str:
    """Template Disclaimer per tipe, semuanya dengan kontak email (fix O2)."""
    e = escape_html
    wn, wu, ce = e(website_name), e(website_url), e(company_email)
    templates = {
        "medical": f"""
            <h1>Medical Disclaimer</h1>
            <p>The information provided by <strong>{wn}</strong> (<a href="{wu}">{wu}</a>) is for general informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.</p>
            <p>If you have any concerns or questions about your health, you should always consult with a physician or other healthcare professional. Do not disregard, avoid, or delay obtaining medical or health-related advice from your healthcare professional because of something you may have read on our website.</p>
        """,
        "financial": f"""
            <h1>Financial Disclaimer</h1>
            <p>All information on this website <strong>{wn}</strong> (<a href="{wu}">{wu}</a>) is published in good faith and for general information purposes only. This website does not offer any financial advice. You should not rely on any information provided on this site to make financial decisions.</p>
            <p>Please consult with a qualified financial advisor before making any investment or financial decisions. <strong>{wn}</strong> will not be liable for any losses or damages in connection with the use of our website.</p>
        """,
        "website": f"""
            <h1>Website Disclaimer</h1>
            <p>The information provided by <strong>{wn}</strong> (<a href="{wu}">{wu}</a>) is for general informational purposes only. We make no representations or warranties, express or implied, regarding the accuracy, adequacy, or completeness of the information on this site.</p>
            <p>Your use of the website and your reliance on any information on the site is solely at your own risk. <strong>{wn}</strong> will not be liable for any losses or damages in connection with the use of our website.</p>
        """,
    }
    body = templates.get(disclaimer_type, f"""
        <h1>General Disclaimer</h1>
        <p>The information provided by <strong>{wn}</strong> (<a href="{wu}">{wu}</a>) is for general informational purposes only. We make no guarantees about the accuracy or completeness of this information. Your use of the site and any information obtained from it is at your own risk.</p>
    """)
    contact = f"""
        <p>Contact us at <a href="mailto:{ce}">{ce}</a> for further inquiries.</p>
        <p>Last updated: {time.strftime("%Y-%m-%d")}</p>
    """
    return body + "\n" + contact


def generate_terms() -> None:
    """Menu interaktif: buat terms_and_conditions.html."""
    print("===== Terms and Conditions Generator =====")
    fields = {
        "website_name": input("Nama Website: ").strip(),
        "website_url": input("URL Website: ").strip(),
        "company_name": input("Nama Perusahaan: ").strip(),
        "governing_law": input("Hukum yang berlaku (misalnya, 'Indonesia'): ").strip(),
        "contact_email": input("Email Kontak Perusahaan: ").strip(),
    }
    output_path = Path.cwd() / "terms_and_conditions.html"
    if not _confirm_overwrite(output_path):
        return
    output_path.write_text(build_terms_and_conditions(**fields), encoding="utf-8")
    print("\nTerms and Conditions telah berhasil dibuat dan disimpan sebagai terms_and_conditions.html.")


def generate_privacy_policy() -> None:
    """Menu interaktif: buat privacy_policy.html."""
    print("=====Privacy Policy Generator=====")
    fields = {
        "website_name": input("Nama Website: ").strip(),
        "website_url": input("URL Website: ").strip(),
        "company_name": input("Nama Perusahaan: ").strip(),
        "company_email": input("Email Kontak Perusahaan: ").strip(),
        "services": input("Layanan yang disediakan (pisahkan dengan koma): ").strip(),
        "third_party_services": input("Layanan pihak ketiga yang digunakan (misalnya Google Analytics, Facebook Pixel): ").strip(),
    }
    output_path = Path.cwd() / "privacy_policy.html"
    if not _confirm_overwrite(output_path):
        return
    output_path.write_text(build_privacy_policy(**fields), encoding="utf-8")
    print("\nPrivacy Policy telah berhasil dibuat dan disimpan sebagai privacy_policy.html.")


def generate_disclaimer() -> None:
    """Menu interaktif: buat disclaimer.html."""
    print("===== Disclaimer Generator Tool =====")
    fields = {
        "website_name": input("Nama Website: ").strip(),
        "website_url": input("URL Website: ").strip(),
        "company_name": input("Nama Perusahaan: ").strip(),
        "company_email": input("Email Kontak Perusahaan: ").strip(),
        "disclaimer_type": input("Jenis Disclaimer (misalnya: 'medical', 'financial', 'website'): ").strip().lower(),
    }
    output_path = Path.cwd() / "disclaimer.html"
    if not _confirm_overwrite(output_path):
        return
    output_path.write_text(build_disclaimer(**fields), encoding="utf-8")
    print("\nDisclaimer telah berhasil dibuat dan disimpan sebagai disclaimer.html.")
