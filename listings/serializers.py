from rest_framework import serializers
from listings.models import Listing, BookingInfo


class ListingSerializer(serializers.ModelSerializer):
    """
    serialize Listing table
    """
    listing_type = serializers.CharField()
    title = serializers.CharField()
    country = serializers.CharField()
    city = serializers.CharField()
    price = serializers.SerializerMethodField(
         method_name='get_price'
    )

    class Meta:
        model = Listing
        depth = 1
        fields = [
            'id', 'listing_type', 'title', 'country', 'city', 'price'
        ]

    def get_price(self, instance):
        return instance.price
