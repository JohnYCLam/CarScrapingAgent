from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CarCriteria(BaseModel):
    make: Optional[str] = Field(None, description="Car manufacturer/brand")
    model: Optional[str] = Field(None, description="Car model")
    year_min: Optional[int] = Field(None, description="Minimum year")
    year_max: Optional[int] = Field(None, description="Maximum year")
    mileage_max: Optional[int] = Field(None, description="Maximum mileage in km")
    price_max: Optional[int] = Field(None, description="Maximum price in dollars")
    location: Optional[str] = Field(None, description="Location/city")
    transmission: Optional[str] = Field(None, description="manual or automatic")
    listing_type: Optional[str] = Field(None, description="new or used")


class ScheduleDetails(BaseModel):
    email: Optional[str] = Field(None, description="User's email address")
    frequency: Optional[str] = Field(None, description="EventBridge schedule expression, e.g., rate(1 day)")
    end_date: Optional[str] = Field(None, description="YYYY-MM-DD")


class ListingInfo(BaseModel):
    make: Optional[str] = Field(None, description="Car manufacturer/brand")
    model: Optional[str] = Field(None, description="Car model")
    year: Optional[int] = Field(None, description="Car year")
    price: Optional[int] = Field(None, description="Price in dollars, numeric only")
    mileage: Optional[int] = Field(None, description="Mileage in km, numeric only")
    location: Optional[str] = Field(None, description="Location or city")


class ListingsBatch(BaseModel):
    listings: List[ListingInfo]
