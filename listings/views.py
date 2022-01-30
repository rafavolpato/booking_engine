import datetime
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet

from listings import serializers
from listings.models import Listing


class UnitViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    Allows only get:
        - get (api/v1/unit/) : get data from Listing using: check_in, check_out and max_price
    """
    # http_method_names = ['get']
    serializer_class = serializers.ListingSerializer
    queryset = Listing.objects.all()

    def get_queryset(self, *args, **kwargs):
        """
        create a queryset to return hotels and apartments
        """
        # if self.kwargs['pk']:
        #     return ValidationError(f"Search by id not allowed")

        pk = self.request.query_params.get('pk', None)
        max_price = self.request.query_params.get('max_price', None)
        check_in = self.request.query_params.get('check_in', None)
        check_out = self.request.query_params.get('check_out', None)

        format = '%Y-%m-%d'
        if check_in:
            try:
                datetime.datetime.strptime(check_in, format)
            except ValueError:
                raise ValidationError(f"Check_in has an incorrect date string format. It should be YYYY-MM-DD")

            if not check_out:
                raise ValidationError(f"Check_out not informed")
            check_in = check_in.replace('-', '')


        if check_out:
            try:
                datetime.datetime.strptime(check_out, format)
            except ValueError:
                raise ValidationError(f"Check_out has an incorrect date string format. It should be YYYY-MM-DD")

            if not check_in:
                raise ValidationError(f"Check_in not informed")
            check_out = check_out.replace('-', '')

        queryset = get_raw_queryset(max_price, check_in, check_out)
        return queryset


def get_raw_queryset(max_price, check_in, check_out):
    dict_params = {'check_in': check_in, 'check_out': check_out, 'max_price': max_price}

    select_clause = 'select "listings_listing"."id", '\
        '"listings_listing"."listing_type", '\
        '"listings_listing"."title", '\
        '"listings_listing"."country", '\
        '"listings_listing"."city", '\
        'CAST(MIN("listings_bookinginfo"."price") AS NUMERIC) AS "price" '

    check_max_price = 'and listings_bookinginfo.price <= :max_price ' if max_price else ' '

    apartment_is_blocked = \
        'and listings_listing.id  not in ( '\
        'select listings_blocked.listing_id '\
        'from listings_blocked '\
        'where listings_listing.id = listing_id '\
        'and ((check_in < :check_in and check_out > :check_in) '\
        'or (check_in < :check_out and check_out > :check_out))) ' if check_in else ' '

    hotel_is_blocked = \
        'and listings_hotelroom.id not in ( ' \
        'select listings_blocked.hotel_room_id ' \
        'from listings_blocked ' \
        'where listings_hotelroom.id = hotel_room_id ' \
        'and ((check_in < :check_in and check_out > :check_in) ' \
        'or (check_in < :check_out and check_out > :check_out))) ' if check_in else ' '

    group_by_clause = 'group by "listings_listing"."id", "listings_listing"."listing_type", ' \
        '"listings_listing"."title", "listings_listing"."country" '

    qs = Listing.objects.raw(
        select_clause +\
        'from listings_hotelroomtype, listings_hotelroom, listings_listing, listings_bookinginfo '\
        'where listings_hotelroomtype.id = listings_hotelroom.hotel_room_type_id '\
        'and listings_hotelroomtype.id = listings_bookinginfo.hotel_room_type_id '\
        'and listings_hotelroomtype.hotel_id = listings_listing.id '\
        'and listings_listing.listing_type = "hotel" '\
        + check_max_price + hotel_is_blocked\
        + group_by_clause +\
        'union '\
        + select_clause +\
        'from listings_listing, listings_bookinginfo '\
        'WHERE listings_listing.id = listings_bookinginfo.listing_id '\
        'and listings_listing.listing_type = "apartment" '\
        + check_max_price + apartment_is_blocked\
        + group_by_clause +\
        'order by price'
        ,
        dict_params)
    return qs


# def get_apartment_queryset(max_price, check_in, check_out):
#     search = Q()
#     if max_price:
#         search.add(Q(booking_info__price__lte=max_price), Q.AND)
#
#     searchBlocked = Q()
#     if check_in:
#         searchBlocked.add(
#             ((Q(check_in__lt=check_in) & Q(check_out__gt=check_in)) |
#              (Q(check_in__lt=check_out) & Q(check_out__gt=check_out))), Q.AND)
#
#     search.add(Q(listing_type='apartment'), Q.AND)
#
#     blocked = Blocked.objects.filter(searchBlocked)
#
#     queryset = Listing.objects.select_related('booking_info').filter(search).filter(
#         ~Exists(blocked.filter(listing_id=OuterRef('pk')))
#     )
#     # order_by('price')
#
#     # queryset = BookingInfo.objects.filter(search).distinct().order_by('price')
#     return queryset


# def get_hotel_queryset(max_price, check_in, check_out):
    # searchBlocked = Q()
    # if check_in:
    #     searchBlocked.add(
    #         ((Q(check_in__lt=check_in) & Q(check_out__gt=check_in)) |
    #          (Q(check_in__lt=check_out) & Q(check_out__gt=check_out))), Q.AND)
    #
    #
    # blocked = Blocked.objects.filter(searchBlocked)
    #
    # hotelroom = HotelRoom.objects.select_related('hotel_room_type').filter(
    #     ~Exists(blocked.filter(hotel_room_id=OuterRef('pk')))
    # )
    #
    # raw_sql = """SELECT * FROM (SELECT * FROM "public"."XKeywords" WHERE pk_id = my_id) as "XK" LEFT OUTER JOIN  "A"."Keywords" as "AK" ON "AK".kw_id = "XK".k_id ;"""
    # XKeywords.objects.raw(raw_sql)


    # bookinginfo_search = Q()
    # if max_price:
    #     bookinginfo_search.add(Q(price__lte=max_price), Q.AND)
    # bookinginfo_search.add(Q(Exists(hotelroom.filter(hotel_room_type_id=OuterRef('pk')))), Q.AND)
    # bookinginfo = BookingInfo.objects\
    #     .select_related('listing')\
    #     .filter(bookinginfo_search) \
    #     .filter(listing__listing_type='hotel') \
    #     .values('listing_id', 'listing__listing_type', 'listing__title', 'listing__country', 'listing__city') \
    #     .annotate(price=Max('price')) \
    #
    # listing = Listing.objects.filter(id__in=bookinginfo)
    # order_by('price')

    # queryset = BookingInfo.objects.filter(search).distinct().order_by('price')
    # return bookinginfo
