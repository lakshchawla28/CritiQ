from django.core.management.base import BaseCommand
from apps.reviews.models import Tag


class Command(BaseCommand):
    help = 'Create initial predefined tags'

    def handle(self, *args, **kwargs):
        tags = [
            # Mood Tags
            {'name': 'Rewatchable', 'category': 'quality'},
            {'name': 'Emotional', 'category': 'mood'},
            {'name': 'Feel-good', 'category': 'mood'},
            {'name': 'Heartwarming', 'category': 'mood'},
            {'name': 'Nostalgic', 'category': 'mood'},
            {'name': 'Hilarious', 'category': 'mood'},
            {'name': 'Dark', 'category': 'mood'},
            {'name': 'Disturbing', 'category': 'mood'},
            {'name': 'Romantic', 'category': 'mood'},
            
            # Pace Tags
            {'name': 'Slow-paced', 'category': 'pace'},
            {'name': 'Action-packed', 'category': 'pace'},
            {'name': 'Fast-paced', 'category': 'pace'},
            {'name': 'Gripping', 'category': 'pace'},
            {'name': 'Intense', 'category': 'pace'},
            {'name': 'Suspenseful', 'category': 'pace'},
            
            # Quality Tags
            {'name': 'Mind-bending', 'category': 'quality'},
            {'name': 'Thought-provoking', 'category': 'quality'},
            {'name': 'Visually Stunning', 'category': 'quality'},
            {'name': 'Epic', 'category': 'quality'},
            {'name': 'Unpredictable', 'category': 'quality'},
            {'name': 'Original', 'category': 'quality'},
            {'name': 'Masterpiece', 'category': 'quality'},
            
            # Theme Tags
            {'name': 'Fun', 'category': 'theme'},
            {'name': 'Inspiring', 'category': 'theme'},
            {'name': 'Philosophical', 'category': 'theme'},
            {'name': 'Political', 'category': 'theme'},
            {'name': 'Psychological', 'category': 'theme'},
            
            # General Tags
            {'name': 'Overrated', 'category': 'general'},
            {'name': 'Underrated', 'category': 'general'},
            {'name': 'Cult Classic', 'category': 'general'},
            {'name': 'Must-Watch', 'category': 'general'},
            {'name': 'Skip It', 'category': 'general'},
            {'name': 'Boring', 'category': 'general'},
            {'name': 'Confusing', 'category': 'general'},
            {'name': 'Predictable', 'category': 'general'},
            {'name': 'Cliché', 'category': 'general'},
            {'name': 'Clever', 'category': 'general'},
            {'name': 'Atmospheric', 'category': 'general'},
            {'name': 'Character-driven', 'category': 'general'},
            {'name': 'Plot-driven', 'category': 'general'},
        ]

        created_count = 0
        for tag_data in tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults=tag_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created tag: {tag.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal tags created: {created_count}')
        )