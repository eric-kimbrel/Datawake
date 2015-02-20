var addon = self;
var panelApp = angular.module('panelApp', ["ngRoute"]).config(['$provide', function ($provide) {
    $provide.decorator('$sniffer', ['$delegate', function ($delegate) {
        $delegate.history = false;
        return $delegate;
    }]);
}]);

$("[name='my-checkbox']").bootstrapSwitch();

panelApp.controller("PanelCtrl", function ($scope, $document) {

    $scope.teamSpinner = true;
    $scope.domainSpinner = true;
    $scope.trailSpinner = true;
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
    $scope.domains = addon.options.domains;
    if (! $scope.domains ) $scope.domains = [];
    $scope.trails = []

    console.log("opening panel for tab: "+addon.options.tabId)
    console.log($scope.datawake)

    // TEAMS
    $scope.teams = [];
    if ($scope.datawake && $scope.datawake.team ) $scope.teams.push($scope.datawake.team)
    $scope.selectedTeam = ($scope.datawake && $scope.datawake.team ) ? $scope.datawake.team : null;

    // when teams are returned  from the server set the selected team as the matching element from the teams array
    addon.port.on("teams",function(teams){
        $scope.teams = teams;
        $scope.selectedTeam = null;
        if ($scope.datawake.team){
            for (i in $scope.teams){
                if ($scope.teams[i].id == $scope.datawake.team.id){
                    $scope.selectedTeam = $scope.teams[i]
                }
            }
        }
        $scope.teamSpinner = false;
        $scope.$apply();
        console.log("GOT TEAMS")
        console.log(teams)
    });

    $scope.teamChanged = function (team) {
        $scope.datawake.team = team;
        $scope.datawake.domain = null;
        $scope.datawake.trail = null;
        $scope.isDatawakeOn = false;
        $scope.domains = []
        $scope.trails = []
        $scope.domainSpinner = true;
        addon.port.emit("changeTeam",{tabId:  addon.options.tabId, team: team});
        console.log("teamChanged")
        console.log($scope.datawake)
    };



    // DOMAINS
    if (! $scope.datawake.team) $scope.domainSpinner = false;
    $scope.domains =[];
    if ($scope.datawake && $scope.datawake.domain ) $scope.domains.push($scope.datawake.domain)
    $scope.selectedDomain = ($scope.datawake && $scope.datawake.domain ) ? $scope.datawake.domian : null;

    // when domains come in from the server set the selected domain to the matching element
    addon.port.on("domains", function (domains) {
        $scope.selectedDomain = null;
        $scope.domains = domains;
        if ( $scope.datawake.domain && $scope.domains){
            for (i in $scope.domains){
                if ($scope.domains[i].id == $scope.datawake.domain.id){
                    $scope.selectedDomain = $scope.domains[i]
                }
            }
        }
        $scope.domainSpinner = false;
        $scope.$apply()
        console.log("GOT DOMAINS")
        console.log(domains)
    });

    $scope.domainChanged = function (domain) {
        $scope.datawake.domain = domain;
        $scope.datawake.trail = null;
        $scope.isDatawakeOn = false;
        $scope.trails = [];
        $scope.trailSpinner = true;
        addon.port.emit("changeDomain",{tabId:  addon.options.tabId, domain: $scope.datawake.domain});
        console.log("domainChanged")
        console.log($scope.datawake)

    };


    // TRAILS
    if ( !$scope.datawake.team || ! $scope.datawake.domain ) $scope.trailSpinner = false;
    $scope.trails = [];
    if ($scope.datawake && $scope.datawake.trail) $scope.trails.push($scope.datawake.trail);
    $scope.selectedTrail = ($scope.datawake && $scope.datawake.trail) ? $scope.datawake.trail : null;

    addon.port.on("trails", function (trails) {
        $scope.trails = trails;
        $scope.selectedTrail = null;
        if ( $scope.datawake.trail && $scope.trails){
            for (i in $scope.trails){
                if ($scope.trails[i].id == $scope.datawake.trail.id){
                    $scope.selectedTrail= $scope.trails[i]
                }
            }
        }
        $scope.trailSpinner = false;
        $scope.$apply();
        console.log("GOT TRAILS")
        console.log(trails)
    });

    $scope.trailChanged = function(trail){
        $scope.datawake.trail = trail;
        $scope.datawake.isDatawakeOn = false;
        addon.port.emit("infochanged",{tabId:  addon.options.tabId, info: $scope.datawake});
        console.log("trailChanged")
        console.log($scope.datawake)
    };


    $scope.newTrail = function(team,domain,newTrailName,newTrailDesc){
        var data = {}
        data.team_id = team.id;
        data.domain_id = domain.id;
        data.name = newTrailName
        data.description = (newTrailDesc) ? newTrailDesc : "";
        $scope.trailChanged(null);
        $scope.newTrailName = null;
        addon.port.emit("createTrail",data);
    }


    addon.port.on("trailCreated",function(trail){
        $scope.trails.push(trail)
        $scope.selectedTrail = trail
        $scope.datawake.trail = trail;
        addon.port.emit("infochanged",{tabId:  addon.options.tabId, info: $scope.datawake});
        $scope.apply()
    });



    // Recording
    $scope.recordingChange = function(recording){
        $scope.datawake.isDatawakeOn = recording;
        addon.port.emit("infochanged",{tabId:  addon.options.tabId, info: $scope.datawake});
        console.log("recordingChange")
        console.log($scope.datawake)
    }



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

    addon.port.on("entities", function (features) {
        console.log(features);
        $scope.extracted_entities_dict = features;
        $scope.$apply();
    });


    addon.port.on("externalLinks", function (links) {
        console.debug("Loading External Entities..");
        $scope.$apply(function () {
            $scope.extracted_tools = links;
        });
    });


    $scope.signOut = function(){
        addon.port.emit("signOut");
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
        if ($scope.entities_in_domain && $scope.entities_in_domain.hasOwnProperty(type)) {
            return $scope.entities_in_domain[type].indexOf(name) >= 0;
        }
    };




   addon.port.on("infosaved",function(datawakeinfo){
        $scope.datawake = datawakeinfo;
        $scope.$apply()
       console.log("ON INFO SAVED")
       console.log($scope.datawake)
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