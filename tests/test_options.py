"""Tests for TakeOptions builder."""

from renderscreenshot.options import TakeOptions


class TestTakeOptionsCreation:
    """Tests for TakeOptions creation methods."""

    def test_url_creates_options(self):
        """Test creating options with a URL."""
        options = TakeOptions.url("https://example.com")
        config = options.to_config()

        assert config["url"] == "https://example.com"

    def test_html_creates_options(self):
        """Test creating options with HTML."""
        options = TakeOptions.html("<h1>Hello</h1>")
        config = options.to_config()

        assert config["html"] == "<h1>Hello</h1>"

    def test_from_config_creates_options(self):
        """Test creating options from a config dict."""
        config = {"url": "https://example.com", "width": 1200}
        options = TakeOptions.from_config(config)

        assert options.to_config()["url"] == "https://example.com"
        assert options.to_config()["width"] == 1200


class TestTakeOptionsImmutability:
    """Tests for TakeOptions immutability."""

    def test_width_returns_new_instance(self):
        """Test that calling a method returns a new instance."""
        options1 = TakeOptions.url("https://example.com")
        options2 = options1.width(1200)

        assert options1 is not options2
        assert "width" not in options1.to_config()
        assert options2.to_config()["width"] == 1200

    def test_chaining_preserves_values(self):
        """Test that chaining methods preserves previous values."""
        options = TakeOptions.url("https://example.com").width(1200).height(630).format("png")
        config = options.to_config()

        assert config["url"] == "https://example.com"
        assert config["width"] == 1200
        assert config["height"] == 630
        assert config["format"] == "png"


class TestTakeOptionsViewport:
    """Tests for viewport options."""

    def test_width(self):
        """Test setting width."""
        options = TakeOptions.url("https://example.com").width(1920)
        assert options.to_config()["width"] == 1920

    def test_height(self):
        """Test setting height."""
        options = TakeOptions.url("https://example.com").height(1080)
        assert options.to_config()["height"] == 1080

    def test_scale(self):
        """Test setting scale."""
        options = TakeOptions.url("https://example.com").scale(2.0)
        assert options.to_config()["scale"] == 2.0

    def test_mobile(self):
        """Test setting mobile mode."""
        options = TakeOptions.url("https://example.com").mobile()
        assert options.to_config()["mobile"] is True

        options_false = TakeOptions.url("https://example.com").mobile(False)
        assert options_false.to_config()["mobile"] is False


class TestTakeOptionsCapture:
    """Tests for capture options."""

    def test_full_page(self):
        """Test full page capture."""
        options = TakeOptions.url("https://example.com").full_page()
        assert options.to_config()["full_page"] is True

    def test_element(self):
        """Test element capture."""
        options = TakeOptions.url("https://example.com").element("#content")
        assert options.to_config()["element"] == "#content"

    def test_format(self):
        """Test format setting."""
        for fmt in ["png", "jpeg", "webp", "pdf"]:
            options = TakeOptions.url("https://example.com").format(fmt)
            assert options.to_config()["format"] == fmt

    def test_quality(self):
        """Test quality setting."""
        options = TakeOptions.url("https://example.com").quality(85)
        assert options.to_config()["quality"] == 85


class TestTakeOptionsWait:
    """Tests for wait options."""

    def test_wait_for(self):
        """Test wait_for condition."""
        for condition in ["load", "networkidle", "domcontentloaded"]:
            options = TakeOptions.url("https://example.com").wait_for(condition)
            assert options.to_config()["wait_for"] == condition

    def test_delay(self):
        """Test delay setting."""
        options = TakeOptions.url("https://example.com").delay(1000)
        assert options.to_config()["delay"] == 1000

    def test_wait_for_selector(self):
        """Test wait_for_selector."""
        options = TakeOptions.url("https://example.com").wait_for_selector(".loaded")
        assert options.to_config()["wait_for_selector"] == ".loaded"

    def test_wait_for_timeout(self):
        """Test wait_for_timeout."""
        options = TakeOptions.url("https://example.com").wait_for_timeout(5000)
        assert options.to_config()["wait_for_timeout"] == 5000


class TestTakeOptionsPresets:
    """Tests for preset options."""

    def test_preset(self):
        """Test preset setting."""
        options = TakeOptions.url("https://example.com").preset("og_card")
        assert options.to_config()["preset"] == "og_card"

    def test_device(self):
        """Test device setting."""
        options = TakeOptions.url("https://example.com").device("iphone_14_pro")
        assert options.to_config()["device"] == "iphone_14_pro"


class TestTakeOptionsBlocking:
    """Tests for blocking options."""

    def test_block_ads(self):
        """Test blocking ads."""
        options = TakeOptions.url("https://example.com").block_ads()
        assert options.to_config()["block_ads"] is True

    def test_block_trackers(self):
        """Test blocking trackers."""
        options = TakeOptions.url("https://example.com").block_trackers()
        assert options.to_config()["block_trackers"] is True

    def test_block_cookie_banners(self):
        """Test blocking cookie banners."""
        options = TakeOptions.url("https://example.com").block_cookie_banners()
        assert options.to_config()["block_cookie_banners"] is True

    def test_block_chat_widgets(self):
        """Test blocking chat widgets."""
        options = TakeOptions.url("https://example.com").block_chat_widgets()
        assert options.to_config()["block_chat_widgets"] is True

    def test_block_urls(self):
        """Test blocking specific URLs."""
        patterns = ["*google-analytics*", "*facebook*"]
        options = TakeOptions.url("https://example.com").block_urls(patterns)
        assert options.to_config()["block_urls"] == patterns

    def test_block_resources(self):
        """Test blocking resource types."""
        resources = ["font", "media"]
        options = TakeOptions.url("https://example.com").block_resources(resources)
        assert options.to_config()["block_resources"] == resources


class TestTakeOptionsPageManipulation:
    """Tests for page manipulation options."""

    def test_inject_script(self):
        """Test injecting script."""
        options = TakeOptions.url("https://example.com").inject_script("alert('hi')")
        assert options.to_config()["inject_script"] == "alert('hi')"

    def test_inject_style(self):
        """Test injecting style."""
        options = TakeOptions.url("https://example.com").inject_style("body{color:red}")
        assert options.to_config()["inject_style"] == "body{color:red}"

    def test_click(self):
        """Test clicking element."""
        options = TakeOptions.url("https://example.com").click(".button")
        assert options.to_config()["click"] == ".button"

    def test_hide(self):
        """Test hiding elements."""
        selectors = [".ad", ".popup"]
        options = TakeOptions.url("https://example.com").hide(selectors)
        assert options.to_config()["hide"] == selectors

    def test_remove(self):
        """Test removing elements."""
        selectors = [".ad", ".popup"]
        options = TakeOptions.url("https://example.com").remove(selectors)
        assert options.to_config()["remove"] == selectors


class TestTakeOptionsBrowserEmulation:
    """Tests for browser emulation options."""

    def test_dark_mode(self):
        """Test dark mode."""
        options = TakeOptions.url("https://example.com").dark_mode()
        assert options.to_config()["dark_mode"] is True

    def test_reduced_motion(self):
        """Test reduced motion."""
        options = TakeOptions.url("https://example.com").reduced_motion()
        assert options.to_config()["reduced_motion"] is True

    def test_media_type(self):
        """Test media type."""
        options = TakeOptions.url("https://example.com").media_type("print")
        assert options.to_config()["media_type"] == "print"

    def test_user_agent(self):
        """Test user agent."""
        ua = "Mozilla/5.0 Custom"
        options = TakeOptions.url("https://example.com").user_agent(ua)
        assert options.to_config()["user_agent"] == ua

    def test_timezone(self):
        """Test timezone."""
        options = TakeOptions.url("https://example.com").timezone("America/New_York")
        assert options.to_config()["timezone"] == "America/New_York"

    def test_locale(self):
        """Test locale."""
        options = TakeOptions.url("https://example.com").locale("fr-FR")
        assert options.to_config()["locale"] == "fr-FR"

    def test_geolocation(self):
        """Test geolocation."""
        options = TakeOptions.url("https://example.com").geolocation(40.7128, -74.0060)
        geo = options.to_config()["geolocation"]
        assert geo["latitude"] == 40.7128
        assert geo["longitude"] == -74.0060

    def test_geolocation_with_accuracy(self):
        """Test geolocation with accuracy."""
        options = TakeOptions.url("https://example.com").geolocation(40.7128, -74.0060, 100.0)
        geo = options.to_config()["geolocation"]
        assert geo["accuracy"] == 100.0


class TestTakeOptionsNetwork:
    """Tests for network options."""

    def test_headers(self):
        """Test custom headers."""
        headers = {"X-Custom": "value", "Accept-Language": "en-US"}
        options = TakeOptions.url("https://example.com").headers(headers)
        assert options.to_config()["headers"] == headers

    def test_cookies(self):
        """Test cookies."""
        cookies = [{"name": "session", "value": "abc123", "domain": "example.com"}]
        options = TakeOptions.url("https://example.com").cookies(cookies)
        assert options.to_config()["cookies"] == cookies

    def test_auth_basic(self):
        """Test basic auth."""
        options = TakeOptions.url("https://example.com").auth_basic("user", "pass")
        auth = options.to_config()["auth_basic"]
        assert auth["username"] == "user"
        assert auth["password"] == "pass"

    def test_auth_bearer(self):
        """Test bearer auth."""
        options = TakeOptions.url("https://example.com").auth_bearer("token123")
        assert options.to_config()["auth_bearer"] == "token123"

    def test_bypass_csp(self):
        """Test bypass CSP."""
        options = TakeOptions.url("https://example.com").bypass_csp()
        assert options.to_config()["bypass_csp"] is True


class TestTakeOptionsCache:
    """Tests for cache options."""

    def test_cache_ttl(self):
        """Test cache TTL."""
        options = TakeOptions.url("https://example.com").cache_ttl(86400)
        assert options.to_config()["cache_ttl"] == 86400

    def test_cache_refresh(self):
        """Test cache refresh."""
        options = TakeOptions.url("https://example.com").cache_refresh()
        assert options.to_config()["cache_refresh"] is True


class TestTakeOptionsPdf:
    """Tests for PDF options."""

    def test_pdf_paper_size(self):
        """Test PDF paper size."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_paper_size("a4")
        assert options.to_config()["pdf_paper_size"] == "a4"

    def test_pdf_dimensions(self):
        """Test PDF width and height."""
        options = (
            TakeOptions.url("https://example.com")
            .format("pdf")
            .pdf_width("8.5in")
            .pdf_height("11in")
        )
        assert options.to_config()["pdf_width"] == "8.5in"
        assert options.to_config()["pdf_height"] == "11in"

    def test_pdf_landscape(self):
        """Test PDF landscape."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_landscape()
        assert options.to_config()["pdf_landscape"] is True

    def test_pdf_margins(self):
        """Test PDF margins."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_margin("1in")
        assert options.to_config()["pdf_margin"] == "1in"

        options_individual = (
            TakeOptions.url("https://example.com")
            .format("pdf")
            .pdf_margin_top("1in")
            .pdf_margin_right("0.5in")
            .pdf_margin_bottom("1in")
            .pdf_margin_left("0.5in")
        )
        config = options_individual.to_config()
        assert config["pdf_margin_top"] == "1in"
        assert config["pdf_margin_right"] == "0.5in"
        assert config["pdf_margin_bottom"] == "1in"
        assert config["pdf_margin_left"] == "0.5in"

    def test_pdf_scale(self):
        """Test PDF scale."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_scale(0.8)
        assert options.to_config()["pdf_scale"] == 0.8

    def test_pdf_print_background(self):
        """Test PDF print background."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_print_background()
        assert options.to_config()["pdf_print_background"] is True

    def test_pdf_page_ranges(self):
        """Test PDF page ranges."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_page_ranges("1-5, 8")
        assert options.to_config()["pdf_page_ranges"] == "1-5, 8"

    def test_pdf_header_footer(self):
        """Test PDF header and footer."""
        options = (
            TakeOptions.url("https://example.com")
            .format("pdf")
            .pdf_header("<div>Header</div>")
            .pdf_footer("<div>Footer</div>")
        )
        assert options.to_config()["pdf_header"] == "<div>Header</div>"
        assert options.to_config()["pdf_footer"] == "<div>Footer</div>"

    def test_pdf_fit_one_page(self):
        """Test PDF fit one page."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_fit_one_page()
        assert options.to_config()["pdf_fit_one_page"] is True

    def test_pdf_prefer_css_page_size(self):
        """Test PDF prefer CSS page size."""
        options = TakeOptions.url("https://example.com").format("pdf").pdf_prefer_css_page_size()
        assert options.to_config()["pdf_prefer_css_page_size"] is True


class TestTakeOptionsStorage:
    """Tests for storage options."""

    def test_storage_enabled(self):
        """Test storage enabled."""
        options = TakeOptions.url("https://example.com").storage_enabled()
        assert options.to_config()["storage_enabled"] is True

    def test_storage_path(self):
        """Test storage path."""
        options = TakeOptions.url("https://example.com").storage_path("screenshots/{hash}.{ext}")
        assert options.to_config()["storage_path"] == "screenshots/{hash}.{ext}"

    def test_storage_acl(self):
        """Test storage ACL."""
        options = TakeOptions.url("https://example.com").storage_acl("public-read")
        assert options.to_config()["storage_acl"] == "public-read"


class TestTakeOptionsToParams:
    """Tests for to_params() method."""

    def test_basic_params(self):
        """Test basic params conversion."""
        options = TakeOptions.url("https://example.com").width(1200).height(630)
        params = options.to_params()

        assert params["url"] == "https://example.com"
        assert params["viewport"]["width"] == 1200
        assert params["viewport"]["height"] == 630

    def test_nested_viewport(self):
        """Test viewport is properly nested."""
        options = TakeOptions.url("https://example.com").width(1200).height(630).scale(2).mobile()
        params = options.to_params()

        assert params["viewport"] == {
            "width": 1200,
            "height": 630,
            "scale": 2,
            "mobile": True,
        }

    def test_nested_pdf(self):
        """Test PDF options are properly nested."""
        options = (
            TakeOptions.url("https://example.com")
            .format("pdf")
            .pdf_paper_size("a4")
            .pdf_landscape()
            .pdf_margin("1in")
        )
        params = options.to_params()

        assert params["pdf"] == {
            "paper_size": "a4",
            "landscape": True,
            "margin": "1in",
        }

    def test_nested_storage(self):
        """Test storage options are properly nested."""
        options = (
            TakeOptions.url("https://example.com")
            .storage_enabled()
            .storage_path("screenshots/{hash}.{ext}")
            .storage_acl("public-read")
        )
        params = options.to_params()

        assert params["storage"] == {
            "enabled": True,
            "path": "screenshots/{hash}.{ext}",
            "acl": "public-read",
        }

    def test_flat_options(self):
        """Test flat options are not nested."""
        options = TakeOptions.url("https://example.com").block_ads().dark_mode().delay(1000)
        params = options.to_params()

        assert params["block_ads"] is True
        assert params["dark_mode"] is True
        assert params["delay"] == 1000


class TestTakeOptionsToQueryString:
    """Tests for to_query_string() method."""

    def test_basic_query_string(self):
        """Test basic query string conversion."""
        options = TakeOptions.url("https://example.com").width(1200)
        query = options.to_query_string()

        assert "url=https" in query
        assert "width=1200" in query

    def test_boolean_lowercase(self):
        """Test booleans are lowercase in query string."""
        options = TakeOptions.url("https://example.com").block_ads().dark_mode()
        query = options.to_query_string()

        assert "block_ads=true" in query
        assert "dark_mode=true" in query

    def test_query_string_encoding(self):
        """Test URL encoding in query string."""
        options = TakeOptions.url("https://example.com/path?query=value")
        query = options.to_query_string()

        # URL should be encoded
        assert "example.com" in query
