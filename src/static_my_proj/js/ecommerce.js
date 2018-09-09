$(document).ready(function() {

  // Contact Form Handler

  var contactForm = $(".contact-form");
  var contactFormMethod = contactForm.attr("method");
  var contactFormEndpoint = contactForm.attr("action");
  
  function displaySubmitting(submitBtn, defaultText, doSubmit) {
    if (doSubmit) {
      submitBtn.addClass("disabled");
      //searchBtn.html("<i class='fas fa-spinner'></i> Searching...");
      submitBtn.html("<i class='fa fa-spin fa-spinner'></i> Sending...");
    } else {
      submitBtn.removeClass("disabled");
      //searchBtn.html("<i class='fas fa-spinner'></i> Searching...");
      submitBtn.html(defaultText);
    }
  }

  contactForm.submit(function(event) {
    event.preventDefault();

    var contactFormSubmitBtn = contactForm.find("[type='submit']");
    var contactFormSubmitBtnTxt = contactFormSubmitBtn.text();

    var contactFormData = contactForm.serialize();
    var thisForm = $(this);
    displaySubmitting(contactFormSubmitBtn, "", true);
    $.ajax({
      method: contactFormMethod,
      url: contactFormEndpoint,
      data: contactFormData,
      success: function(data) {

        setTimeout(function() {
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)}, 500);

        contactForm[0].reset();
        $.alert({
          title: "Success!",
          content: data.message,
          theme: "modern"});
      },
      error: function(errorData) {
        console.log(errorData.responseJSON);

        setTimeout(function() {
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)}, 500);

        var jsonData = errorData.responseJSON;
        var msg = "";

        $.each(jsonData, function(key, value) { // key, value VS array index, object
          msg += key + ": " + value[0].message + "<br/>";
        });

        $.alert({
          title: "Oops!",
          content: msg,
          theme: "modern"});

      }
    })
  })






  // Auto Search
  var searchForm = $(".search-form");
  var searchInput = searchForm.find("[name='q']"); // input name='q'
  var typingTimer;
  var searchingTimer;
  var typingInterval = 500; // .5 seconds
  var searchBtn = searchForm.find("[type='submit']");

  searchInput.keyup(function(event) {
    // console.log(searchInput.val());
    clearTimeout(typingTimer);
    typingTimer = setTimeout(performSearch, typingInterval);
  });

  searchInput.keydown(function(event) {
    clearTimeout(typingTimer);
  })

  function displaySearching() {
    searchBtn.addClass("disabled");
    //searchBtn.html("<i class='fas fa-spinner'></i> Searching...");
    searchBtn.html("<i class='fa fa-spin fa-spinner'></i> Searching...");
  }

  function performSearch() {
    displaySearching();
    var query = searchInput.val();
    searchingTimer = setTimeout(function() {
      window.location.href='/search/?q=' + query;
    }, typingInterval);
  }







  // Cart + Add Products
  var productForm = $(".form-product-ajax"); // #form-product-ajax

  function getOwnedProduct(productId) {
    // $.ajax({
    //   url: actionEndpoint,
    //   method: httpMethod,
    //   data: formData,
    //   success: function(data){

    //   },
    //   error: function(){

    //   }
    // })
    if (productId == 11) {
      return true;
    }
    return false;
  }

  $.each(productForm, function(index, object) {
    var $this = $(this);
    var isUser = $this.attr("data-user");
    var submitSpan = $this.find(".submit-span");
    var productInput = $this.find("[name='product_id']");
    var productId = productInput.attr("value");
    var productIsDigital = productInput.attr("data-is-digital");
    if (isUser && productIsDigital) {
      var isOwned = getOwnedProduct(productId)
      if (isOwned) {
        submitSpan.html("<a href='/library/'>In Library</a>");
      }
    }
  });

  productForm.submit(function(event) {
    event.preventDefault();
    console.log("Form is not sending");
    var thisForm = $(this);
    var actionEndpoint;
    var httpMethod;
    var formData;

    // actionEndpoint = thisForm.attr("action"); // API Endpoint
    actionEndpoint = thisForm.attr("data-endpoint");
    httpMethod = thisForm.attr("method");
    formData = thisForm.serialize();
    console.log(actionEndpoint, httpMethod);

    $.ajax({
      url: actionEndpoint,
      method: httpMethod,
      data: formData,
      success: function(data) {
        var submitSpan = thisForm.find(".submit-span");
        if (data.added) {
          submitSpan.html("<div class='btn-group'><a class='btn btn-link' href='/cart/'>In cart</a> <button type='submit' class='btn btn-link'>Remove?</button></div>");
        } else {
          submitSpan.html("<button class='btn btn-success'>Add to cart</button>");
        }
        var navbarCount = $(".navbar-cart-count");
        navbarCount.text(data.cart_item_count);
        var currentPath = window.location.href;
        if (currentPath.indexOf("cart") != -1) {
          refreshCart(data.removed, data.cart_product_id);
        }
      },
      error: function(errorData) {
        $.alert({
          title: "Oops!",
          content: "An error occurred.",
          theme: "modern"});
        console.log("ajax error: ", errorData);
      }
    });

  });

  function refreshCart(removed, cart_product_id) {
    console.log("in current cart");
    var cartTable = $(".cart-table");
    var cartTableBody = cartTable.find(".cart-table-body");
    //cartTableBody.html("<h1>Changed</h1>")
    var cartProducts = cartTableBody.find(".cart-product");
    var currentUrl = window.location.href;

    if (removed) {
      var cartProductToRemoveClass = ".cart-product-id-" + cart_product_id;
      var cartProductToRemove = cartTableBody.find(cartProductToRemoveClass);
      cartProductToRemove.remove();
    }

    var refreshCartUrl = '/api/cart/';
    var refreshCartMethod = "GET";
    var data = {};
    $.ajax({
      url: refreshCartUrl,
      method: refreshCartMethod,
      data: data,
      success: function(data) {
        console.log("success");
        console.log(data);
        var hiddenCartItemRemoveForm = $(".cart-item-remove-form");
        if (data.products.length > 0) {
          //cartProducts.html("<tr><td colspan=3>Coming Soon</td></tr>");
          // cartProducts.remove();
          // i = data.products.length;
          // $.each(data.products, function(index, value) {
          //   var newCartItemRemove = hiddenCartItemRemoveForm.clone();
          //   newCartItemRemove.css("display", "block");
          //   // newCartItemRemove.removeClass("hiden-class");
          //   newCartItemRemove.find(".cart-item-product-id").val(value.id);
          //   cartTableBody.prepend("<tr><th scope=\"row\">" + i + "</th><td><a href='" + value.url + "'>" + value.name + "</a>" + newCartItemRemove.html() + "</td><td>" + value.price + "</td></tr>");
          //   i--;
          // });
          cartTableBody.find(".cart-subtotal").text(data.subtotal);
          cartTableBody.find(".cart-total").text(data.total);
        } else {
          window.location.href = currentUrl;
        }
      },
      error: function(errorData) {
        $.alert({
          title: "Oops!",
          content: "An error occurred.",
          theme: "modern"});
        console.log("error");
        console.log(errorData);
      }
    });
  }
});