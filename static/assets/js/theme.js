/*-----------------------------------------------------------------------------------
    
    Template Name: AIcraft - AI Application & Generator HTML Template
    Author:  SolverWp
    Support: support.solverwp@gmail.com
    Description: AIcraft - AI Application & Generator HTML Template
    Version: 1.0

    Note: This is Main Js file
-----------------------------------------------------------------------------------
    Js INDEX
    ===================
    ## Main Menu
    ## Document Ready
    ## Nav Overlay
    ## Preloader
    ## Sticky
    ## Back to top
    ## Magnific-popup js
    ## Slick Slider
    ## Isotope Js
    ## WOW Js
    
-----------------------------------------------------------------------------------*/

(function($) {
    'use strict';

    //===== Main Menu

    function mainMenu() {
        
        // Variables
        var var_window = $(window),
        navContainer = $('.header-navigation'),
        navbarToggler = $('.navbar-toggler'),
        navMenu = $('.ac-nav-menu'),
        navMenuLi = $('.ac-nav-menu ul li ul li'),
        closeIcon = $('.navbar-close');

        // navbar toggler
        navbarToggler.on('click', function() {
            navbarToggler.toggleClass('active');
            navMenu.toggleClass('menu-on');
        });

        // close icon
        closeIcon.on('click', function() {
            navMenu.removeClass('menu-on');
            navbarToggler.removeClass('active');
        });

        // adds toggle button to li items that have children
        navMenu.find("li a").each(function() {
            if ($(this).children('.dd-trigger').length < 1) {
                if ($(this).next().length > 0) {
                    $(this).append('<span class="dd-trigger"><i class="far fa-angle-down"></i></span>')
                }
            }
        });

        // expands the dropdown menu on each click
        navMenu.find(".dd-trigger").on('click', function(e) {
            e.preventDefault();
            $(this).parent().parent().siblings().children('ul.submenu').slideUp();
            $(this).parent().next('ul.submenu').stop(!0, !0).slideToggle(350);
            $(this).toggleClass('sub-menu-open')
        });

        // check browser width in real-time
        function breakpointCheck() {
            var windowWidth = window.innerWidth;
            if (windowWidth <= 1199) {
                navContainer.addClass('breakpoint-on');
            }
            else {
                navContainer.removeClass('breakpoint-on');
            }
        }
        breakpointCheck();
        var_window.on('resize', function() {
            breakpointCheck();
        });
    };

    // Document Ready
    $(document).ready(function() {
        mainMenu();
    });


    // Nav Overlay On

    $(".navbar-toggler,.nav-overlay").on('click', function (e) {
        $(".nav-overlay").toggleClass("active");
    });
    $(".nav-overlay").on('click', function (e) {
        $(".navbar-toggler").removeClass("active");
        $(".ac-nav-menu").removeClass("menu-on");
    });


    //===== Preloader
    
    $(window).on('load', function(event) {
        $('.ac-preloader').delay(500).fadeOut('500');
    })
    
    //===== Sticky

    $(window).on('scroll', function(event) {
        var scroll = $(window).scrollTop();
        if (scroll < 100) {
            $(".header-navigation").removeClass("sticky");
        } else {
            $(".header-navigation").addClass("sticky");
        }
    });

    //===== Back to top

    $(window).on('scroll', function(event) {
        if ($(this).scrollTop() > 600) {
            $('.back-to-top').fadeIn(200)
        } else {
            $('.back-to-top').fadeOut(200)
        }
    });
    $('.back-to-top').on('click', function(event) {
        event.preventDefault();
        $('html, body').animate({
            scrollTop: 0,
        }, 1500);
    });


    //===== Magnific-popup js
    
    if ($('.video-popup').length){
        $('.video-popup').magnificPopup({
            type: 'iframe',
            removalDelay: 300,
            mainClass: 'mfp-fade'
        });
    }

    if ($('.img-popup').length){
        $(".img-popup").magnificPopup({
            type: "image",
             gallery: { 
              enabled: true 
            }
        });
    }
    
    //===== Slick slider js

    if ($('.testimonial-slider').length) {
        $('.testimonial-slider').slick({
            dots: false,
            arrows: false,
            infinite: true,
            speed: 800,
            autoplay: true,
            slidesToShow: 3,
            slidesToScroll: 1,
            prevArrow: '<div class="prev"><i class="far fa-arrow-left"></i></div>',
            nextArrow: '<div class="next"><i class="far fa-arrow-right"></i></div>',
            responsive: [
                {
                    breakpoint: 1200,
                    settings: {
                        slidesToShow: 2
                    }
                },
                {
                    breakpoint: 767,
                    settings: {
                        slidesToShow: 1
                    }
                }
            ]
        });
    }
    if ($('.clients-slider').length) {
        $('.clients-slider').slick({
            dots: false,
            arrows: false,
            infinite: true,
            speed: 800,
            autoplay: true,
            slidesToShow: 7,
            slidesToScroll: 1,
            prevArrow: '<div class="prev"><i class="far fa-arrow-left"></i></div>',
            nextArrow: '<div class="next"><i class="far fa-arrow-right"></i></div>',
            responsive: [
                {
                    breakpoint: 1200,
                    settings: {
                        slidesToShow: 4
                    }
                },
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 3
                    }
                }
            ]
        });
    }
    if ($('.clients-slider-two').length) {
        $('.clients-slider-two').slick({
            dots: false,
            arrows: false,
            infinite: true,
            speed: 800,
            autoplay: true,
            slidesToShow: 9,
            slidesToScroll: 1,
            prevArrow: '<div class="prev"><i class="far fa-arrow-left"></i></div>',
            nextArrow: '<div class="next"><i class="far fa-arrow-right"></i></div>',
            responsive: [
                {
                    breakpoint: 1200,
                    settings: {
                        slidesToShow: 4
                    }
                },
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 3
                    }
                }
            ]
        });
    }

    //====== Isotope js

    $('.filter-nav-items li').on('click', function () {
        $(this).siblings('.active').removeClass('active');
        $(this).addClass('active');
        var filterValue = $(this).attr('data-filter');
        $('.isotope-grid').isotope({ filter: filterValue });
    });

    if ($('.ac-isotope').length) {
        $('.ac-isotope').imagesLoaded(function () {
            $('.isotope-grid').isotope({
                itemSelector: '.isotope-filter-item',
                layoutMode: 'fitRows'
            })
        });
    }


    //===== Wow js
    
    new WOW().init();


})(window.jQuery);