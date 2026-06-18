from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def from_pagination(cls, pagination, per_page):
        return cls(
            page=pagination.page,
            per_page=per_page,
            total=pagination.total,
            pages=pagination.pages,
            has_next=pagination.has_next,
            has_prev=pagination.has_prev,
        )