from django.core.management.base import BaseCommand
from apps.social.models import Achievement


class Command(BaseCommand):
    help = 'Create initial achievements'

    def handle(self, *args, **kwargs):
        achievements = [
            # Watching Achievements
            {
                'name': 'First Watch',
                'description': 'Watch your first movie',
                'icon': '🎬',
                'category': 'watching',
                'rarity': 'common',
                'points': 10,
                'criteria': {'movies_watched': 1}
            },
            {
                'name': 'Movie Buff',
                'description': 'Watch 10 movies',
                'icon': '🍿',
                'category': 'watching',
                'rarity': 'common',
                'points': 25,
                'criteria': {'movies_watched': 10}
            },
            {
                'name': 'Cinephile',
                'description': 'Watch 50 movies',
                'icon': '🎥',
                'category': 'watching',
                'rarity': 'rare',
                'points': 50,
                'criteria': {'movies_watched': 50}
            },
            {
                'name': 'Century Club',
                'description': 'Watch 100 movies',
                'icon': '💯',
                'category': 'watching',
                'rarity': 'rare',
                'points': 100,
                'criteria': {'movies_watched': 100}
            },
            {
                'name': 'Movie Master',
                'description': 'Watch 500 movies',
                'icon': '👑',
                'category': 'watching',
                'rarity': 'epic',
                'points': 250,
                'criteria': {'movies_watched': 500}
            },
            {
                'name': 'Legendary Viewer',
                'description': 'Watch 1000 movies',
                'icon': '⭐',
                'category': 'watching',
                'rarity': 'legendary',
                'points': 500,
                'criteria': {'movies_watched': 1000}
            },
            
            # Reviewing Achievements
            {
                'name': 'First Review',
                'description': 'Write your first review',
                'icon': '✍️',
                'category': 'reviewing',
                'rarity': 'common',
                'points': 10,
                'criteria': {'reviews_written': 1}
            },
            {
                'name': 'Critic',
                'description': 'Write 10 reviews',
                'icon': '📝',
                'category': 'reviewing',
                'rarity': 'common',
                'points': 25,
                'criteria': {'reviews_written': 10}
            },
            {
                'name': 'Pro Reviewer',
                'description': 'Write 50 reviews',
                'icon': '🎭',
                'category': 'reviewing',
                'rarity': 'rare',
                'points': 50,
                'criteria': {'reviews_written': 50}
            },
            {
                'name': 'Review Master',
                'description': 'Write 100 reviews',
                'icon': '🏆',
                'category': 'reviewing',
                'rarity': 'epic',
                'points': 100,
                'criteria': {'reviews_written': 100}
            },
            {
                'name': 'Legendary Critic',
                'description': 'Write 500 reviews',
                'icon': '🌟',
                'category': 'reviewing',
                'rarity': 'legendary',
                'points': 250,
                'criteria': {'reviews_written': 500}
            },
            
            # Social Achievements
            {
                'name': 'Popular',
                'description': 'Get 10 likes on your reviews',
                'icon': '❤️',
                'category': 'social',
                'rarity': 'common',
                'points': 20,
                'criteria': {'total_likes': 10}
            },
            {
                'name': 'Influencer',
                'description': 'Get 100 likes on your reviews',
                'icon': '💫',
                'category': 'social',
                'rarity': 'rare',
                'points': 50,
                'criteria': {'total_likes': 100}
            },
            {
                'name': 'Viral Star',
                'description': 'Get 1000 likes on your reviews',
                'icon': '🚀',
                'category': 'social',
                'rarity': 'epic',
                'points': 150,
                'criteria': {'total_likes': 1000}
            },
            {
                'name': 'Rising Star',
                'description': 'Get 10 followers',
                'icon': '🌠',
                'category': 'social',
                'rarity': 'common',
                'points': 20,
                'criteria': {'followers': 10}
            },
            {
                'name': 'Community Leader',
                'description': 'Get 50 followers',
                'icon': '👥',
                'category': 'social',
                'rarity': 'rare',
                'points': 50,
                'criteria': {'followers': 50}
            },
            {
                'name': 'Celebrity',
                'description': 'Get 100 followers',
                'icon': '🎪',
                'category': 'social',
                'rarity': 'epic',
                'points': 100,
                'criteria': {'followers': 100}
            },
            {
                'name': 'Icon',
                'description': 'Get 1000 followers',
                'icon': '💎',
                'category': 'social',
                'rarity': 'legendary',
                'points': 300,
                'criteria': {'followers': 1000}
            },
            
            # Seasonal/Special Achievements
            {
                'name': 'Early Adopter',
                'description': 'Join in the first month',
                'icon': '🎉',
                'category': 'special',
                'rarity': 'rare',
                'points': 50,
                'criteria': {'join_date': 'first_month'}
            },
            {
                'name': 'Marathon Runner',
                'description': 'Watch 10 movies in one day',
                'icon': '🏃',
                'category': 'special',
                'rarity': 'epic',
                'points': 100,
                'criteria': {'movies_in_day': 10}
            },
            {
                'name': 'Night Owl',
                'description': 'Watch 5 movies after midnight',
                'icon': '🦉',
                'category': 'special',
                'rarity': 'rare',
                'points': 30,
                'criteria': {'late_night_watches': 5}
            },
            {
                'name': 'Genre Explorer',
                'description': 'Watch movies from 10 different genres',
                'icon': '🗺️',
                'category': 'special',
                'rarity': 'rare',
                'points': 40,
                'criteria': {'unique_genres': 10}
            },
            {
                'name': 'Time Traveler',
                'description': 'Watch movies from 5 different decades',
                'icon': '⏰',
                'category': 'special',
                'rarity': 'rare',
                'points': 40,
                'criteria': {'unique_decades': 5}
            },
        ]

        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created achievement: {achievement.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal achievements created: {created_count}')
        )