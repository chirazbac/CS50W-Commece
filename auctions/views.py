from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Category, Listing, Comment, Bid
from django.contrib.auth.decorators import login_required


def index(request):
    activeList = Listing.objects.filter(isActive = True)
    listCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
      "listings" : activeList,
      "categories" : listCategories
    }
    )
def listing(request, id):
     listingDetails = Listing.objects.get(pk = id)
     isListInWatchList = request.user in listingDetails.watchlist.all()
     is_Owner = request.user.username == listingDetails.owner.username
     comments = Comment.objects.filter(listing=listingDetails )
     return render(request, "auctions/listingDetails.html",{
     "listing" : listingDetails,
     "isListInWatchList" : isListInWatchList,
     "is_Owner" : is_Owner,
     "comments" : comments

     })

@login_required
def closeAuction(request,id):
    listingDetails = Listing.objects.get(pk = id)
    listingDetails.isActive = False
    isListInWatchList = request.user in listingDetails.watchlist.all()
    is_Owner = request.user.username == listingDetails.owner.username
    comments = Comment.objects.filter(listing=listingDetails )
    listingDetails.save()
    return render(request, "auctions/listingDetails.html", {
                      "listing" : listingDetails,
                      "isListInWatchList" : isListInWatchList,
                      "comments" : comments,
                      "is_Owner" : is_Owner,
                      "message": "Congrats your auction is closed",
                      "bid_updated" : True
                })

@login_required
def addNewComment(request, id):
    user = request.user
    listingDetails = Listing.objects.get(pk=id)
    message = request.POST['newComment']
    newComment = Comment(
    message = message,
    author = user,
    listing = listingDetails
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))

@login_required
def addBid(request, id):
    newAmount = request.POST['newBid']
    listingDetails = Listing.objects.get(pk=id)
    comments = Comment.objects.filter(listing=listingDetails )
    isListInWatchList = request.user in listingDetails.watchlist.all()
    is_Owner = request.user.username == listingDetails.owner.username
    if int(newAmount) > listingDetails.price.amount:
       updatedBid = Bid(user=request.user, amount=int(newAmount))
       updatedBid.save()
       listingDetails.price = updatedBid
       listingDetails.save()
       return render(request, "auctions/listingDetails.html", {
                  "listing" : listingDetails,
                  "isListInWatchList" : isListInWatchList,
                  "comments" : comments,
                  "is_Owner" : is_Owner,
                  "message": "Yeah! Your bid is accepted",
                  "bid_updated" : True
            })

    else:
        return render(request, "auctions/listingDetails.html", {
                             "listing" : listingDetails,
                              "comments" : comments,
                              "is_Owner" : is_Owner,
                              "message": "Sorry! Your bid is refused",
                              "bid_updated" : False
                         })

@login_required
def displayWatchList (request):
     user = request.user
     listings = user.listingWatchList.all()
     return render(request, "auctions/watchlist.html", {
     "listings" : listings

     })

def displayCategory(request):
    if request.method == "POST":
        selected_category = request.POST['category']
        category = Category.objects.get(categoryName = selected_category)
        activeList = Listing.objects.filter(isActive = True , category=category)
        listCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
          "listings" : activeList,
          "categories" : listCategories
        }
        )


def createListing(request):
    if request.method == "GET":
        listCategories = Category.objects.all()
        return render(request, "auctions/createListing.html",{
            "categories" : listCategories
        })
    else:
        title = request.POST['title']
        print(title)
        description = request.POST['description']
        imageURL = request.POST['imageUrl']
        price = request.POST['price']
        category = request.POST['category']
        owner = request.user
        categoryData = Category.objects.get(categoryName = category)
        bid = Bid(
        amount=int(price),
        user = owner)

        bid.save()
        newListing = Listing(
            title = title,
            description = description,
            imageUrl = imageURL,
            price = bid,
            category = categoryData,
            owner = owner
        )
        print(newListing)
        newListing.save()
        return HttpResponseRedirect(reverse(index))

@login_required
def removeWatchList(request, id):
     listingDetails = Listing.objects.get(pk=id)
     user = request.user
     listingDetails.watchlist.remove(user)
     return HttpResponseRedirect(reverse("listing", args=(id, )))


@login_required
def addWatchList(request, id):
    listingData = Listing.objects.get(pk=id)
    user = request.user
    listingData.watchlist.add(user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
