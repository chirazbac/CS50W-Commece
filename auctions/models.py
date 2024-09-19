from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length = 64)
    def __str__(self):
        return self.categoryName

class Bid(models.Model):
      amount = models.IntegerField(default =0)
      user = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True, related_name="Bid_user")
      def __str__(self):
              return f"{self.amount}"

class Listing(models.Model):
      title = models.CharField(max_length = 64)
      description = models.CharField(max_length = 500)
      imageUrl = models.CharField(max_length= 500)
      price = models.ForeignKey(Bid, on_delete = models.CASCADE, blank=True, related_name="listingBid")
      isActive = models.BooleanField(default= True)
      owner = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, related_name="user")
      category = models.ForeignKey(Category, on_delete = models.CASCADE, blank=True, related_name="category")
      watchlist = models.ManyToManyField(User, blank=True, related_name="listingWatchList")

      def __str__(self):
        return self.title

class Comment(models.Model):
      message = models.CharField(max_length=500)
      author = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, related_name="CommentUser")
      listing = models.ForeignKey(Listing, on_delete = models.CASCADE, blank=True, related_name="CommentListing")

      def __str__(self):
              return f"{self.author} comment on {self.listing}"
