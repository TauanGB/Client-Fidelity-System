from dataclasses import dataclass
from pathlib import Path

from django.core.exceptions import ValidationError


@dataclass(frozen=True)
class ImageRequirement:
    label: str
    recommended_size: str
    minimum_width: int
    minimum_height: int
    max_size_mb: int
    allowed_extensions: tuple[str, ...]
    aspect_ratio_min: float
    aspect_ratio_max: float
    usage_hint: str

    @property
    def allowed_extensions_text(self):
        return ", ".join(ext.upper().replace(".", "") for ext in self.allowed_extensions)

    @property
    def help_text(self):
        return (
            f"{self.label}: use {self.allowed_extensions_text}, ate {self.max_size_mb} MB. "
            f"Recomendado {self.recommended_size}. "
            f"Minimo {self.minimum_width}x{self.minimum_height}px. "
            f"{self.usage_hint}"
        )


IMAGE_REQUIREMENTS = {
    "company_logo": ImageRequirement(
        label="Logo",
        recommended_size="512x512 px",
        minimum_width=400,
        minimum_height=400,
        max_size_mb=2,
        allowed_extensions=(".png", ".jpg", ".jpeg", ".webp"),
        aspect_ratio_min=0.9,
        aspect_ratio_max=1.1,
        usage_hint="Imagem quadrada para nao distorcer em avatares e cabecalhos.",
    ),
    "company_banner": ImageRequirement(
        label="Banner",
        recommended_size="1600x600 px",
        minimum_width=1200,
        minimum_height=450,
        max_size_mb=3,
        allowed_extensions=(".png", ".jpg", ".jpeg", ".webp"),
        aspect_ratio_min=2.4,
        aspect_ratio_max=3.2,
        usage_hint="Imagem horizontal ampla para evitar cortes agressivos nas telas publicas.",
    ),
    "reward_image": ImageRequirement(
        label="Imagem da recompensa",
        recommended_size="1200x1200 px",
        minimum_width=800,
        minimum_height=800,
        max_size_mb=2,
        allowed_extensions=(".png", ".jpg", ".jpeg", ".webp"),
        aspect_ratio_min=0.9,
        aspect_ratio_max=1.1,
        usage_hint="Imagem quadrada para exibir o premio sem deformacao.",
    ),
}


def _read_file_header(uploaded_file, size=64):
    if not uploaded_file:
        return b""
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    header = uploaded_file.read(size)
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    return header


def get_image_metadata(uploaded_file):
    header = _read_file_header(uploaded_file)
    if len(header) < 16:
        raise ValidationError("Arquivo de imagem invalido ou incompleto.")

    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        width = int.from_bytes(header[16:20], "big")
        height = int.from_bytes(header[20:24], "big")
        return "png", width, height

    if header.startswith(b"\xff\xd8"):
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        data = uploaded_file.read()
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        index = 2
        sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while index + 8 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            if marker in sof_markers:
                height = int.from_bytes(data[index + 5:index + 7], "big")
                width = int.from_bytes(data[index + 7:index + 9], "big")
                return "jpeg", width, height
            segment_length = int.from_bytes(data[index + 2:index + 4], "big")
            index += 2 + segment_length
        raise ValidationError("Nao foi possivel ler as dimensoes do JPEG enviado.")

    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        chunk = header[12:16]
        if chunk == b"VP8X" and len(header) >= 30:
            width = 1 + int.from_bytes(header[24:27], "little")
            height = 1 + int.from_bytes(header[27:30], "little")
            return "webp", width, height
        if chunk == b"VP8 " and len(header) >= 30:
            width = int.from_bytes(header[26:28], "little") & 0x3FFF
            height = int.from_bytes(header[28:30], "little") & 0x3FFF
            return "webp", width, height
        if chunk == b"VP8L" and len(header) >= 25:
            bits = int.from_bytes(header[21:25], "little")
            width = (bits & 0x3FFF) + 1
            height = ((bits >> 14) & 0x3FFF) + 1
            return "webp", width, height
        raise ValidationError("Nao foi possivel ler as dimensoes do WEBP enviado.")

    raise ValidationError("Formato de imagem nao suportado. Use PNG, JPG, JPEG ou WEBP.")


def validate_image_requirements(uploaded_file, requirement_key):
    if not uploaded_file:
        return uploaded_file

    requirement = IMAGE_REQUIREMENTS[requirement_key]
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in requirement.allowed_extensions:
        raise ValidationError(
            f"Formato invalido para {requirement.label.lower()}. "
            f"Use {requirement.allowed_extensions_text}."
        )

    max_size_bytes = requirement.max_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        raise ValidationError(f"{requirement.label} excede {requirement.max_size_mb} MB.")

    _, width, height = get_image_metadata(uploaded_file)
    if width < requirement.minimum_width or height < requirement.minimum_height:
        raise ValidationError(
            f"{requirement.label} precisa ter ao menos "
            f"{requirement.minimum_width}x{requirement.minimum_height}px."
        )

    ratio = width / height
    if not (requirement.aspect_ratio_min <= ratio <= requirement.aspect_ratio_max):
        raise ValidationError(
            f"{requirement.label} deve seguir proporcao compativel com o layout. "
            f"Recomendado: {requirement.recommended_size}."
        )

    return uploaded_file
