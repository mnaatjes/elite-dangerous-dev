from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import httpx

class ChecksumMetadata(BaseModel):
    # We set default=None inside Field to tell the type checker it's truly optional
    digest: Optional[str] = Field(default=None, alias="Digest")
    content_digest: Optional[str] = Field(default=None, alias="Content-Digest")
    repr_digest: Optional[str] = Field(default=None, alias="Repr-Digest")
    content_md5: Optional[str] = Field(default=None, alias="Content-MD5")
    etag: Optional[str] = Field(default=None, alias="ETag")
    goog_hash: Optional[str] = Field(default=None, alias="x-goog-hash")
    s3_sha256: Optional[str] = Field(default=None, alias="x-amz-meta-sha256")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_headers(cls, headers: httpx.Headers):
        """
        By using model_validate, we bypass the __init__ signature checks 
        that cause VSCode errors.
        """
        header_data = {
            "digest": headers.get("Digest"),
            "content_digest": headers.get("Content-Digest"),
            "repr_digest": headers.get("Repr-Digest"),
            "content_md5": headers.get("Content-MD5"),
            "etag": headers.get("ETag"),
            "goog_hash": headers.get("x-goog-hash"),
            "s3_sha256": headers.get("x-amz-meta-sha256"),
        }
        # model_validate is the best practice for Pydantic v2
        return cls.model_validate(header_data)

    # --- Debugging Methods ---

    def to_dict(self, by_alias: bool = False):
        """
        Converts the model to a Python dictionary.
        Set by_alias=True if you want the keys to be the HTTP Header names.
        """
        return self.model_dump(by_alias=by_alias, exclude_none=True)

    def to_json(self, indent: int = 4):
        """
        Converts the model to a pretty-printed JSON string.
        """
        # exclude_none=True keeps the output clean by removing null fields
        return self.model_dump_json(indent=indent, exclude_none=True)