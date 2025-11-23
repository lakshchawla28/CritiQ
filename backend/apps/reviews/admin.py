from django.contrib import admin
from .models import Review, ReviewLike, ReviewComment, ReviewRepost


# ------------------------------
# Inline Admins
# ------------------------------

class ReviewLikeInline(admin.TabularInline):
    model = ReviewLike
    extra = 0
    readonly_fields = ("user", "created_at")


class ReviewCommentInline(admin.TabularInline):
    model = ReviewComment
    fk_name = "review"
    extra = 0
    readonly_fields = ("user", "comment_text", "created_at", "updated_at")


class ReviewRepostInline(admin.TabularInline):
    model = ReviewRepost
    fk_name = "original_review"
    extra = 0
    readonly_fields = ("user", "comment", "created_at")


# ------------------------------
# Review Admin
# ------------------------------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "movie",
        "rating",
        "privacy",
        "likes_count",
        "comments_count",
        "reposts_count",
        "created_at",
    )

    list_filter = (
        "rating",
        "privacy",
        "contains_spoilers",
        "created_at",
    )

    search_fields = (
        "user__username",
        "movie__title",
        "review_text",
        "tags",
    )

    readonly_fields = (
        "likes_count",
        "comments_count",
        "reposts_count",
        "created_at",
        "updated_at",
    )

    inlines = [ReviewLikeInline, ReviewCommentInline, ReviewRepostInline]

    ordering = ("-created_at",)


# ------------------------------
# Standalone Admins (in case needed)
# ------------------------------

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "review", "created_at")
    search_fields = ("user__username", "review__id")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "review", "parent_comment", "created_at")
    search_fields = ("user__username", "review__id", "comment_text")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReviewRepost)
class ReviewRepostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "original_review", "created_at")
    search_fields = ("user__username", "original_review__id")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
