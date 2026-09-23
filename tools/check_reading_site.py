"""Built-site QA. See README.md for dependency and preview setup."""

import argparse
import json
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

from playwright.sync_api import expect, sync_playwright


def page_paths(site_dir):
    if not (site_dir / "index.html").is_file():
        raise SystemExit(f"Build the site first: {site_dir / 'index.html'} is missing")
    pages = []
    for path in sorted(site_dir.rglob("*.html")):
        relative = path.relative_to(site_dir).as_posix()
        if relative == "404.html":
            continue
        pages.append("/" + relative.removesuffix("index.html"))
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--site-dir", type=Path, default=Path("site"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/notes-site-qa"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"pages": [], "errors": [], "bad_links": [], "interactions": {}}
    try:
        check_site(args, report)
    except Exception as error:
        report["errors"].append(f"{type(error).__name__}: {error}")
        raise
    finally:
        (args.output / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))


def check_site(args, report):
    BASE = args.base_url.rstrip("/")
    OUTPUT = args.output
    PAGES = page_paths(args.site_dir)
    links = set()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        page = context.new_page()
        page.on("pageerror", lambda error: report["errors"].append(str(error)))
        for mode, width, height in [("desktop", 1440, 1000), ("mobile", 390, 844)]:
            page.set_viewport_size({"width": width, "height": height})
            for path in PAGES:
                response = page.goto(BASE + path, wait_until="domcontentloaded")
                page.wait_for_function("[...document.images].every(i => i.complete)")
                if page.locator(".mermaid").count():
                    page.wait_for_selector(".mermaid svg")
                if page.locator(".arithmatex").count():
                    page.wait_for_function("document.querySelector('mjx-container') !== null", timeout=30000)
                    page.evaluate("MathJax.startup.promise")
                result = page.evaluate("""() => ({
                    width: innerWidth,
                    documentWidth: document.documentElement.scrollWidth,
                    brokenImages: [...document.images].filter(i => i.getAttribute('src') && !i.naturalWidth).map(i => i.src),
                    figures: document.querySelectorAll('.paper-figure').length,
                    linkedCaptions: document.querySelectorAll('.paper-figure figcaption a').length,
                    math: document.querySelectorAll('mjx-container').length,
                    mathErrors: [...document.querySelectorAll('mjx-merror')].map(e => e.textContent),
                    links: [...document.querySelectorAll('a[href]')].map(a => a.href),
                    routes: [...document.querySelectorAll('.study-route')].map(route => ({
                        tag: route.firstElementChild?.tagName,
                        items: [...(route.querySelector('ol')?.children ?? [])].map(item => ({
                            tag: item.tagName,
                            height: item.getBoundingClientRect().height,
                            link: Boolean(item.querySelector('a[href]')),
                            separated: getComputedStyle(item).borderBottomStyle !== 'none'
                        }))
                    }))
                })""")
                links.update(result.pop("links"))
                result.update({"path": path, "mode": mode, "status": response.status})
                report["pages"].append(result)
                assert response.status == 200, result
                assert result["documentWidth"] <= width, result
                assert not result["brokenImages"] and not result["mathErrors"], result
                assert result["linkedCaptions"] >= result["figures"], result
                for route in result["routes"]:
                    assert route["tag"] == "OL" and route["items"], result
                    assert all(item["tag"] == "LI" and item["height"] >= 44
                               and item["link"] and item["separated"] for item in route["items"]), result
                if path in ("/", "/zju/", "/research/video_generation/") or path.endswith(("architectures/", "minimax_h3/")):
                    name = path.strip("/").replace("/", "_") or "home"
                    page.screenshot(path=str(OUTPUT / f"{mode}_{name}.png"))

        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(BASE, wait_until="domcontentloaded")
        for name, path in [("ZJU", "/zju/"), ("CMU 15-445", "/cmu_15_445/")]:
            page.locator(".md-tabs").get_by_role("link", name=name, exact=True).click()
            assert urlparse(page.url).path == path, page.url
        report["interactions"]["section_indexes"] = "passed"

        for term, expected in [("数据库", "/zju/database_system/"),
                               ("ARIES", "/cmu_15_445/recovery_with_aries/"),
                               ("VAE 视频", "/research/video_generation/video_vae/")]:
            search = page.get_by_role("textbox", name="搜索", exact=True)
            # Reopen the overlay explicitly after Escape; fill alone can leave
            # the result list hidden while the input still retains focus.
            search.click()
            search.fill("")
            search.press("ArrowLeft")
            expect(page.locator(".md-search-result__meta")).to_have_text("键入以开始搜索")
            search.fill(term)
            search.press("ArrowLeft")
            page.locator(f'.md-search-result a[href*="{expected}"]').first.wait_for(state="visible")
            search.press("Escape")
        report["interactions"]["search"] = "passed"

        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(BASE + "/research/video_generation/video_vae/", wait_until="domcontentloaded")
        fields = page.locator("[data-token-tool] input")
        outputs = page.locator("[data-token-tool] output")
        assert outputs.nth(0).inner_text() == "10,200"
        page.locator("[data-token-tool] select").select_option("32")
        assert outputs.nth(0).inner_text() == "2,550"
        fields.nth(0).fill("18")
        assert page.locator(".token-error").inner_text()
        assert outputs.nth(0).inner_text() == "—"
        fields.nth(0).fill("17")
        assert outputs.nth(0).inner_text() == "2,550"
        fields.nth(0).fill("")
        assert page.locator(".token-error").inner_text()
        fields.nth(0).fill("17")
        fields.nth(1).fill("")
        assert page.locator(".token-error").inner_text()
        fields.nth(1).fill("544")
        report["interactions"]["calculator"] = "passed"

        page.locator(".paper-figure a:has(img)").first.click()
        assert page.locator("dialog").evaluate("d => d.open")
        page.screenshot(path=str(OUTPUT / "mobile_figure_dialog.png"))
        page.keyboard.press("Escape")
        assert not page.locator("dialog").evaluate("d => d.open")
        page.locator(".paper-figure a:has(img)").first.click()
        page.get_by_role("button", name="关闭原图").click()
        assert not page.locator("dialog").evaluate("d => d.open")
        report["interactions"]["figure_dialog"] = "passed"

        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(BASE + "/research/video_generation/architectures/", wait_until="domcontentloaded")
        page.wait_for_function("[...document.images].every(i => i.complete)")
        page.wait_for_function("document.querySelector('mjx-container') !== null")
        page.evaluate("MathJax.startup.promise")
        page.get_by_title("切换到暗色模式", exact=True).click()
        page.wait_for_function("document.body.dataset.mdColorScheme === 'slate'")
        page.locator(".paper-figure").first.scroll_into_view_if_needed()
        page.screenshot(path=str(OUTPUT / "desktop_dark_figure.png"))
        report["interactions"]["dark_mode"] = page.locator("body").get_attribute("data-md-color-scheme")
        assert report["interactions"]["dark_mode"] == "slate"

        documents = {}
        for link in sorted(links):
            parsed = urlparse(link)
            if parsed.netloc != urlparse(BASE).netloc or parsed.scheme not in ("http", "https"):
                continue
            document_url = link.split("#")[0]
            if document_url not in documents:
                response = context.request.get(document_url)
                is_html = "text/html" in response.headers.get("content-type", "")
                ids = set()
                if response.status == 200 and is_html:
                    soup = BeautifulSoup(response.text(), "html.parser")
                    ids = {element["id"] for element in soup.select("[id]")}
                documents[document_url] = (response.status, is_html, ids)
            status, is_html, ids = documents[document_url]
            if status != 200:
                report["bad_links"].append({"url": link, "status": status})
            elif parsed.fragment and is_html and unquote(parsed.fragment) not in ids:
                report["bad_links"].append({"url": link, "reason": "anchor missing"})
        browser.close()

    assert not report["errors"] and not report["bad_links"]


if __name__ == "__main__":
    main()
