from django.contrib import admin
from .models import Post, Achievement, UserAchievement, YearlyStats


# ============================================================
#                       POST ADMIN
# ============================================================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_content", "likes_count",
                    "comments_count", "created_at")
    search_fields = ("user__username", "content")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    readonly_fields = ("likes_count", "comments_count",
                       "created_at", "updated_at")

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content Preview"


# ============================================================
#                   ACHIEVEMENT ADMIN
# ============================================================
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "rarity", "points", "created_at")
    search_fields = ("name", "description")
    list_filter = ("category", "rarity")
    ordering = ("name",)


# ============================================================
#                USER ACHIEVEMENT ADMIN
# ============================================================
@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement", "earned_at", "progress")
    search_fields = ("user__username", "achievement__name")
    list_filter = ("earned_at", "achievement__category", "achievement__rarity")
    ordering = ("-earned_at",)

    readonly_fields = ("earned_at",)


# ============================================================
#                   YEARLY STATS ADMIN
# ============================================================
@admin.register(YearlyStats)
class YearlyStatsAdmin(admin.ModelAdmin):
    list_display = ("user", "year", "movies_watched", "reviews_written",
                    "likes_received", "new_followers")
    search_fields = ("user__username",)
    list_filter = ("year",)
    ordering = ("-year",)

    readonly_fields = ("created_at",)
