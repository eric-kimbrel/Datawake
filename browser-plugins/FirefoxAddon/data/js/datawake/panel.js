var addon = self;
var panelApp = angular.module('panelApp', ["ngRoute"]).config(['$provide', function ($provide) {
    $provide.decorator('$sniffer', ['$delegate', function ($delegate) {
        $delegate.history = false;
        return $delegate;
    }]);
}]);

$("[name='my-checkbox']").bootstrapSwitch();

panelApp.controller("PanelCtrl", function ($scope, $document) {

    $scope.extracted_tools = [];
    $scope.datawake = addon.options.datawakeInfo;
    $scope.current_url = addon.options.current_url;
    $scope.domainFeaturesEnabled = addon.options.useDomainFeatures;
    $scope.rankingEnabled = addon.options.useRanking;
    $scope.versionNumber = addon.options.versionNumber;
    $scope.user = addon.options.userInfo;
    $scope.invalid = {};
    $scope.pageVisits = addon.options.pageVisits;
    $scope.headerPartial = "partials/header-partial.html";



    // TEAMS

    // set the selected team from the users teams array based on matching ids.
    // for UI to work correctly the selectedTeam is matched by reference to the team in user.teams
    $scope.selectedTeam = null;
    if ($scope.datawake.team){
        for (i in $scope.user.teams){
            if ($scope.user.teams[i].id == $scope.datawake.team.id){
                $scope.selectedTeam = $scope.user.teams[i]
            }
        }
    }

    $scope.teamChanged = function (team) {
        var info = addon.options.datawakeInfo;
        info.team = team;
        addon.port.emit("infochanged",{tabId:  addon.options.tabId, info: info});
    };



    // DOMAINS


    addon.port.on("sendDomains", function (domains) {
        $scope.domains = domains;
        $scope.$apply();
    });

    $scope.domainChanged = function (domain) {
        var selected = domain.name;
        if (selected != null && selected != "") {
            addon.port.emit("getTrails", selected);
            $scope.selectedTrail = null;
        }
    };


    addon.port.on("sendTrails", function (trails) {
        $scope.trails = trails;
        $scope.$apply();
    });


    addon.port.on("feedbackEntities", function (entities) {
        $scope.$apply(function () {
            $scope.feedbackEntities = entities;
        });
    });


    addon.port.on("ranking", function (rankingInfo) {
        $scope.$apply(function () {
            $scope.ranking = rankingInfo.ranking;
            var starRating = $("#star_rating");
            starRating.attr("data-average", rankingInfo.ranking);
            createStarRating(addon.options.starUrl);
        });
    });

    addon.port.on("entities", function (extractedEntities) {
        $scope.$apply(function () {
            console.debug("Parsing Extracted Entities...");
            $scope.extracted_entities_dict = extractedEntities.allEntities;
            $scope.entities_in_domain = extractedEntities.domainExtracted;
        });
    });


    addon.port.on("externalLinks", function (links) {
        console.debug("Loading External Entities..");
        $scope.$apply(function () {
            $scope.extracted_tools = links;
        });
    });


    $scope.signOut = function(){
        addon.port.emit("signout");
    }

    $scope.openExternalLink = function (externalUrl) {
        addon.port.emit("openExternalLink", {externalUrl: externalUrl});
    };

    $scope.markInvalid = function (type, entity) {
        var postObj = {};
        postObj.entity_type = type;
        postObj.entity_value = entity;
        postObj.domain = $scope.datawake.domain.name;
        addon.port.emit("markInvalid", postObj);
    };

    addon.port.on("marked", function (entity) {
        $scope.$apply(function () {
            $scope.invalid[entity] = true;
        });
    });

    $scope.isExtracted = function (type, name) {
        if ($scope.entities_in_domain.hasOwnProperty(type)) {
            return $scope.entities_in_domain[type].indexOf(name) >= 0;
        }
    };

    $scope.record = function(recording){
        var info = addon.options.datawakeInfo;
        info.isDatawakeOn = recording;
        addon.port.emit("infochanged",{tabId:  addon.options.tabId, info: info});
    }




    addon.port.on("infosaved",function(datawakeinfo){
        $scope.datawake = datawakeinfo;
        $scope.$apply()
    })

    function createStarRating(starUrl) {
        var starRating = $("#star_rating");
        starRating.jRating({
            type: 'big', // type of the rate.. can be set to 'small' or 'big'
            length: 10, // nb of stars
            rateMax: 10,
            bigStarsPath: starUrl + 'stars.png',
            smallStarsPath: starUrl + 'small.png',
            sendRequest: false,
            canRateAgain: true,
            nbRates: 9999999,
            onClick: function (element, rate) {
                setUrlRank(rate);
                $scope.$apply(function () {
                    $scope.ranking = rate;
                });
            }
        });

    }

    function setUrlRank(rank) {
        var rank_data = {
            domain: $scope.datawake.domain.name,
            trailname: $scope.datawake.trail.name,
            rank: rank
        };
        addon.port.emit("setUrlRank", rank_data);
    }

    addon.port.emit("init");

});

panelApp.config(['$routeProvider',
    function ($routeProvider) {
        $routeProvider.
            when('/features/all', {
                templateUrl: 'partials/extracted-entities-partial.html'
            }).
            when('/features/domain', {
                templateUrl: 'partials/domain-extracted-partial.html'
            }).
            when('/feedback', {
                templateUrl: 'partials/feedback-partial.html'
            }).
            otherwise({
                redirectTo: '/features/domain'
            });
    }]);