import base64

from app.services.extraction import get_medio_cargue, get_source_type
from app.services.preprocessors import encode_image_to_base64, extract_text_from_excel


class TestGetSourceType:
    def test_pdf(self):
        assert get_source_type("application/pdf") == "documento"

    def test_image_png(self):
        assert get_source_type("image/png") == "imagen"

    def test_image_jpeg(self):
        assert get_source_type("image/jpeg") == "imagen"

    def test_audio_mpeg(self):
        assert get_source_type("audio/mpeg") == "audio"

    def test_audio_wav(self):
        assert get_source_type("audio/wav") == "audio"

    def test_text_plain(self):
        assert get_source_type("text/plain") == "documento"

    def test_excel(self):
        assert get_source_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") == "documento"

    def test_unknown(self):
        assert get_source_type("application/octet-stream") == "desconocido"


class TestGetMedioCargue:
    def test_pdf(self):
        assert get_medio_cargue("application/pdf") == "documento"

    def test_image(self):
        assert get_medio_cargue("image/png") == "imagen"

    def test_audio(self):
        assert get_medio_cargue("audio/mpeg") == "audio"

    def test_text(self):
        assert get_medio_cargue("text/plain") == "documento"

    def test_excel(self):
        assert get_medio_cargue("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") == "documento"


class TestEncodeImageToBase64:
    def test_returns_data_uri(self):
        raw = b"\x89PNG\r\n\x1a\n"
        result = encode_image_to_base64(raw, "image/png")
        assert result.startswith("data:image/png;base64,")
        # Verify the base64 payload decodes back
        payload = result.split(",", 1)[1]
        assert base64.b64decode(payload) == raw


class TestExtractTextFromExcel:
    def test_reads_single_sheet(self):
        import openpyxl
        import io

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["concepto", "valor"])
        ws.append(["arriendo", 1500000])
        buf = io.BytesIO()
        wb.save(buf)

        text = extract_text_from_excel(buf.getvalue())
        assert "arriendo" in text
        assert "1500000" in text

    def test_empty_workbook(self):
        import openpyxl
        import io

        wb = openpyxl.Workbook()
        # Default sheet is empty
        buf = io.BytesIO()
        wb.save(buf)

        text = extract_text_from_excel(buf.getvalue())
        assert text == ""
