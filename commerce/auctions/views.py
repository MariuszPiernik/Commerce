from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment,Bid

def listing(request,id):
    listingData= Listing.objects.get(pk = id)
    isListingInWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    if(request.user.username== listingData.owner.username):
        isOwner = True
    else:
        isOwner= False
    return render(request, "auctions/listing.html",{
        "listing" : listingData,
        "isListingInWatchList": isListingInWatchList,
        "allComments": allComments,
        "isOwner": isOwner
    })

def closeAuction(request,id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isListingInWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html",{
        "listing" : listingData,
        "isListingInWatchList": isListingInWatchList,
        "allComments": allComments,
        "isOwener": isOwner,
        "update": True,
        "message" : "Auctions is closed!"
    })

def addBid(request,id):
    if request.method == "POST":
        newBid = request.POST["newBid"]
        listingData =Listing.objects.get(pk=id)
        isOwner = request.user.username == listingData.owner.username
        isListingInWatchList = request.user in listingData.watchlist.all()
        allComments = Comment.objects.filter(listing=listingData)
        if (newBid!='') and(int(newBid) > listingData.price.bid):
            updateBid = Bid(user=request.user, bid=newBid)
            updateBid.save()
            listingData.price=updateBid
            listingData.save()

            return render(request, "auctions/listing.html",{
                "listing":listingData,
                "message": "Bid was updated successfully",
                "update":True,
                "isListingInWatchList": isListingInWatchList,
                "allComments": allComments,
                "isOwner": isOwner,
            })

        else:
            return render(request, "auctions/listing.html",{
                "listing":listingData,
                "message": "Bid updated failed",
                "update":False,
                "isListingInWatchList": isListingInWatchList,
                "allComments": allComments,
                "isOwener": isOwner,

                })



def addComment(request,id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]

    newComment = Comment(
        author = currentUser,
        listing = listingData,
        message = message

    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

def removeWatchlist(request,id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))
def addWatchlist(request,id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def index(request):
    activeListings= Listing.objects.filter(isActive = True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings" : activeListings,
        "categories":categories
    })
def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListings= Listing.objects.filter(isActive = True,category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings" : activeListings,
            "categories":categories
        })


def listing_creator(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories":categories
        })
    else:
        title =request.POST["title"]
        description = request.POST["description"]
        image =request.POST["image"]
        price =request.POST["price"]
        category =request.POST["category"]
        user = request.user
        categoryData = Category.objects.get(categoryName = category)
        bid = Bid(bid = float(price), user=user)
        bid.save()
        newListing = Listing(
            title=title,
            description = description,
            price = bid,
            photo = image,
            category = categoryData,
            owner = user,
        )
        newListing.save()
        return HttpResponseRedirect(reverse(index))

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
