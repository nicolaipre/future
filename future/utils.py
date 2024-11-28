def decode_header(headers: list[tuple[bytes]]):
    """Decode request headers"""
    return [(key.decode("utf-8"), value.decode("utf-8")) for key, value in headers]
