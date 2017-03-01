# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IpropertyItem(scrapy.Item):
    # define the fields for your item here like:
    
    CarParks = scrapy.Field()
    Facilities = scrapy.Field()
    
    QuikProNo = scrapy.Field()
    PropertyType = scrapy.Field()
    Tenure = scrapy.Field()
    BuiltUp = scrapy.Field()
    AskingPrice = scrapy.Field()
    Bedrooms = scrapy.Field()
    Bathrooms = scrapy.Field()
    Occupancy = scrapy.Field()
    Furnishing = scrapy.Field()
    PostedDate = scrapy.Field()
    FacingDirection = scrapy.Field()
    MaintenanceFee = scrapy.Field()
    LandArea = scrapy.Field()
    AskingPricepsf = scrapy.Field()
    ReservedPrice = scrapy.Field()
    AuctionDate = scrapy.Field()
    DateAvailable = scrapy.Field()
    ReferenceNo = scrapy.Field()
    UnexpLeaseYr = scrapy.Field()
    
    isSale = scrapy.Field()
    listingID = scrapy.Field()
    mapLat = scrapy.Field()
    mapLon = scrapy.Field()
    buildingID = scrapy.Field()
    buildingName = scrapy.Field()
    propertyType = scrapy.Field()
    state = scrapy.Field()
    area = scrapy.Field()
    township = scrapy.Field()
    address = scrapy.Field()
    ownerName = scrapy.Field()
    ownerPhone = scrapy.Field()
    userName = scrapy.Field()
    userEmail = scrapy.Field()
    userCellPhone = scrapy.Field()
    price = scrapy.Field()
    displayTitle = scrapy.Field()
    image = scrapy.Field()
    askingPrice = scrapy.Field()
    protype = scrapy.Field()
    stateCode = scrapy.Field()
    cauroselAgentListing = scrapy.Field()
    cauroselAgentArea = scrapy.Field()
    reportListingURL = scrapy.Field()
    isOwner = scrapy.Field()
    cauroselSale = scrapy.Field()
    cauroselRent = scrapy.Field()

    
    #agent_name = scrapy.Field()
    #agent_contact = scrapy.Field()
    #area = scrapy.Field()
    #image = scrapy.Field()
    
