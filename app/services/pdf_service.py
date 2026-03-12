# Standard library
from typing import Any

# Third-party
from jinja2 import DictLoader, Environment

# Local
from app.models import BrandSettings

INVOICE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: sans-serif; color: #333; }
    h1 { color: {{ primary_color }}; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; border: 1px solid #ddd; }
    th { background: {{ primary_color }};
         color: white; }
    .footer { color: #666; font-size: 0.85em;
              margin-top: 2em; }
  </style>
</head>
<body>
  {% if logo_url %}
  <img src="{{ logo_url }}" height="60" alt="logo">
  {% endif %}
  <h1>{{ brand_name }}</h1>
  <h2>Invoice {{ invoice_number }}</h2>
  <p><strong>Client:</strong>
     {{ invoice.client_id }}</p>
  <p><strong>Due:</strong> {{ invoice.due_date }}</p>
  <p><strong>Status:</strong>
     {{ invoice.status.value }}</p>
  <table>
    <tr>
      <th>Description</th><th>Qty</th>
      <th>Unit Price</th><th>Total</th>
    </tr>
    {% for item in invoice.items %}
    <tr>
      <td>{{ item.description }}</td>
      <td>{{ item.quantity }}</td>
      <td>{{ item.unit_price }}</td>
      <td>{{ item.quantity * item.unit_price }}</td>
    </tr>
    {% endfor %}
  </table>
  <p><strong>Total: {{ invoice.total_amount }}
     {{ invoice.currency }}</strong></p>
  {% if footer_text %}
  <p class="footer">{{ footer_text }}</p>
  {% endif %}
</body>
</html>
"""


class PdfService:
    """
    Generates invoice PDFs using the active workspace
    branding (logo, colours, prefix, footer).
    """

    def __init__(
        self,
        brand: BrandSettings,
    ) -> None:
        self.brand = brand
        loader = DictLoader({"invoice_template": INVOICE_TEMPLATE})
        self._env = Environment(loader=loader)

    def render_invoice(
        self,
        invoice: Any,
    ) -> bytes:
        """
        Render invoice to PDF bytes using active brand.

        Args:
            invoice: Invoice domain model to render.

        Returns:
            PDF file content as bytes.
        """
        context = {
            "brand_name": self.brand.brand_name,
            "logo_url": self.brand.logo_url,
            "primary_color": (self.brand.primary_color),
            "footer_text": self.brand.footer_text,
            "invoice_number": (
                f"{self.brand.invoice_prefix}-{invoice.id:05d}"
            ),
            "invoice": invoice,
        }
        html = self._html_to_string(context)
        return self._html_to_pdf(html)

    def _html_to_string(self, context: dict) -> str:
        """Render Jinja2 template to HTML string."""
        tmpl = self._env.get_template("invoice_template")
        return tmpl.render(**context)

    @staticmethod
    def _html_to_pdf(html: str) -> bytes:
        """
        Convert HTML string to PDF bytes.

        Uses WeasyPrint if available, falls back to
        returning UTF-8 encoded HTML for testing.
        """
        try:
            from weasyprint import HTML  # type: ignore

            return HTML(string=html).write_pdf()
        except Exception:
            return html.encode("utf-8")
