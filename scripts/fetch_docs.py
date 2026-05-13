"""
Fetches Polish business law documents from public government sources.

For your portfolio demo, you can:
1. Use the sample URLs below (real Polish gov pages)
2. OR replace with any other public legal/policy PDFs
3. OR use product documentation if you want a SaaS-flavored demo

Output: data/raw/*.txt files ready for indexing.
"""
import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Sample sources. Replace with your own — these are illustrative.
# For best results, use 10-30 documents totaling 200-2000 pages.
SOURCES = [
    # Core government
    {
        "name": "biznes_gov_jdg",
        "url": "https://biznes.gov.pl/en/portal/001823",
        "type": "html",
        "description": "Official Polish government guide to registering and running a sole proprietorship (JDG), including CEIDG registration, obligations, and requirements"
    },
    {
        "name": "biznes_gov_vat",
        "url": "https://www.biznes.gov.pl/en/portal/004160",
        "type": "html",
        "description": "Official explanation of VAT registration rules, thresholds (including 200,000 PLN exemption), and when VAT registration is required"
    },
    {
        "name": "biznes_gov_contracts",
        "url": "https://biznes.gov.pl/pl/portal/00115",
        "type": "html",
        "description": "Government guidance on civil law contracts, B2B cooperation, and legal forms of providing services in Poland"
    },
    {
        "name": "gov_services",
        "url": "https://www.gov.pl/web/gov/uslugi-dla-przedsiebiorcy",
        "type": "html",
        "description": "Central government portal listing online public services for entrepreneurs, including registration, tax filings, and administrative procedures"
    },

    # Tax authority (KAS)
    {
        "name": "podatki_main",
        "url": "https://www.podatki.gov.pl",
        "type": "html",
        "description": "Official Polish National Tax Administration portal providing comprehensive information on taxes, obligations, and compliance"
    },
    {
        "name": "vat_registration",
        "url": "https://www.podatki.gov.pl/vat/rejestracja-do-vat/",
        "type": "html",
        "description": "Detailed official rules for VAT registration, including when registration is mandatory or optional"
    },
    {
        "name": "vat_basics",
        "url": "https://www.podatki.gov.pl/podatki-firmowe/vat/informacje-podstawowe/",
        "type": "html",
        "description": "Fundamental VAT concepts including taxable activities, taxpayers, and scope of VAT in Poland"
    },
    {
        "name": "business_tax",
        "url": "https://www.podatki.gov.pl/podatki-firmowe/",
        "type": "html",
        "description": "Overview of business taxation in Poland, including VAT, PIT, and other obligations for entrepreneurs"
    },
    {
        "name": "starting_business_tax",
        "url": "https://www.podatki.gov.pl/dzialalnosc-gospodarcza/",
        "type": "html",
        "description": "Tax obligations and requirements when starting and operating a business in Poland"
    },
    {
        "name": "vat_ue",
        "url": "https://www.podatki.gov.pl/dzialalnosc-gospodarcza/podatnik-vat-ue/",
        "type": "html",
        "description": "Rules for intra-EU VAT (VAT-UE), including registration, reporting, and cross-border transactions"
    },
    {
        "name": "pit_info",
        "url": "https://www.podatki.gov.pl/pit/",
        "type": "html",
        "description": "Official information on personal income tax (PIT), including rates, forms of taxation, and filing obligations"
    },

    # ZUS
    {
        "name": "zus_main",
        "url": "https://www.zus.pl",
        "type": "html",
        "description": "Official Social Insurance Institution portal covering social security rules and obligations in Poland"
    },
    {
        "name": "zus_firms",
        "url": "https://www.zus.pl/firmy",
        "type": "html",
        "description": "Guidance for businesses on social insurance contributions, deadlines, and reporting requirements"
    },
    {
        "name": "zus_entrepreneurs",
        "url": "https://www.zus.pl/przedsiebiorcy",
        "type": "html",
        "description": "Information for entrepreneurs on ZUS registration, contribution schemes, and relief programs"
    },

    # Registries
    {
        "name": "ceidg",
        "url": "https://prod.ceidg.gov.pl",
        "type": "html",
        "description": "Official registry of sole proprietors (JDG) in Poland, including registration, updates, and public records"
    },
    {
        "name": "gus_api",
        "url": "https://api.stat.gov.pl",
        "type": "api",
        "description": "Central Statistical Office API providing access to REGON business registry and official statistical data"
    },
    {
        "name": "krs_registry",
        "url": "https://wyszukiwarka-krs.ms.gov.pl",
        "type": "html",
        "description": "National Court Register (KRS) search system for companies and legal entities in Poland"
    },

    # Legal acts (ISAP)
    {
        "name": "vat_act",
        "url": "https://isap.sejm.gov.pl/isap.nsf/docdetails.xsp?id=WDU20040540535",
        "type": "html",
        "description": "Polish VAT Act defining VAT rules, taxable events, rates, exemptions, and obligations"
    },
    {
        "name": "pit_act",
        "url": "https://isap.sejm.gov.pl/isap.nsf/docdetails.xsp?id=WDU19910800350",
        "type": "html",
        "description": "Personal Income Tax Act regulating income taxation, rates, deductions, and reporting obligations"
    },
    {
        "name": "entrepreneurs_law",
        "url": "https://isap.sejm.gov.pl/isap.nsf/docdetails.xsp?id=WDU20180000646",
        "type": "html",
        "description": "Entrepreneurs Law governing business activity, rights, obligations, and rules for economic activity"
    },
    {
        "name": "civil_code",
        "url": "https://isap.sejm.gov.pl/isap.nsf/docdetails.xsp?id=WDU19640160093",
        "type": "html",
        "description": "Civil Code regulating contracts, obligations, liability, and general private law relationships"
    },
    {
        "name": "accounting_act",
        "url": "https://isap.sejm.gov.pl/isap.nsf/docdetails.xsp?id=WDU19941210591",
        "type": "html",
        "description": "Accounting Act defining bookkeeping rules, financial reporting, and accounting obligations"
    },

    # VAT tools
    {
        "name": "vat_whitelist",
        "url": "https://www.podatki.gov.pl/wykaz-podatnikow-vat/",
        "type": "html",
        "description": "Official VAT taxpayer whitelist for verifying VAT status and bank accounts of businesses"
    },
    {
        "name": "jpk_reporting",
        "url": "https://www.podatki.gov.pl/jpk/",
        "type": "html",
        "description": "Information on JPK (Standard Audit File for Tax), including reporting obligations and file structures"
    },

    # Advanced legal sources
    {
        "name": "tax_interpretations",
        "url": "https://interpretacje-podatkowe.org",
        "type": "html",
        "description": "Database of individual tax rulings issued by Polish authorities, covering practical tax interpretations and edge cases"
    },
    {
        "name": "administrative_court",
        "url": "https://orzeczenia.nsa.gov.pl",
        "type": "html",
        "description": "Database of administrative court judgments, including tax and business law cases"
    },

    # EU context
    {
        "name": "eu_tax",
        "url": "https://taxation-customs.ec.europa.eu",
        "type": "html",
        "description": "European Commission portal on taxation and customs, including EU VAT rules and cross-border regulations"
    },
    {
        "name": "vies",
        "url": "https://ec.europa.eu/taxation_customs/vies/",
        "type": "html",
        "description": "EU VAT Information Exchange System (VIES) for validating VAT numbers of EU businesses"
    }
    # Add more sources here. For a strong demo, aim for 15-30 documents.
    # You can also drop PDFs directly into data/raw/ as .txt files
    # (extract text first with: pdftotext file.pdf file.txt)
]


def clean_html(html: str) -> str:
    """Extract readable text from HTML, dropping nav/scripts/ads."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def fetch_one(src: dict) -> None:
    """Download one source and save as a clean .txt file."""
    out_path = RAW_DIR / f"{src['name']}.txt"
    if out_path.exists():
        print(f"  [skip] {src['name']} already exists")
        return

    print(f"  [fetch] {src['name']} ← {src['url']}")
    try:
        r = requests.get(src["url"], timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (RAG portfolio demo; respectful crawler)"
        })
        r.raise_for_status()
    except Exception as e:
        print(f"  [error] {src['name']}: {e}")
        return

    if src["type"] == "html":
        text = clean_html(r.text)
    else:
        text = r.text

    # Prepend metadata so it survives chunking
    header = f"SOURCE: {src['url']}\nTITLE: {src['description']}\n\n"
    out_path.write_text(header + text, encoding="utf-8")
    print(f"  [ok] saved {len(text):,} chars to {out_path.name}")


def main() -> None:
    print(f"Fetching {len(SOURCES)} sources into {RAW_DIR}/")
    for src in SOURCES:
        fetch_one(src)

    # Sanity check — count what we have
    files = list(RAW_DIR.glob("*.txt"))
    total_chars = sum(f.stat().st_size for f in files)
    print(f"\nDone. {len(files)} files, {total_chars:,} bytes total.")
    if len(files) < 5:
        print("\nWARNING: You have very few documents. Add more sources to SOURCES")
        print("or drop additional .txt files into data/raw/ manually.")


if __name__ == "__main__":
    main()
