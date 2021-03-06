'use strict';


// Declare app level module which depends on filters, and services
angular.module('act', [
    'ngRoute',
    'ngCookies',
    'angularFileUpload',
    'act.filters',
    'act.services',
    'act.directives',
    'act.controllers',
    'ngMaterial'
]).
    constant('urls', {
        'part': '/static/partials',
        'api': '/api',
        'host': location.protocol.concat('//').concat(window.location.hostname.concat(location.port?':'+location.port:''))
    }).
    config(['$interpolateProvider', function($interpolateProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }]).
    config(['$httpProvider', function($httpProvider){
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    }]).
    config(['$routeProvider', '$locationProvider', 'urls', function($routeProvider, $locationProvider, urls) {
        //Route configure
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix = '';
        $routeProvider.when('/', {templateUrl: urls.part + '/homepage.html', controller: 'HomepageCtrl', title: '个人主页'});
        $routeProvider.when('/user/login', {templateUrl: urls.part + '/login.html', controller: 'UserLoginCtrl', title: '登陆'});
        $routeProvider.when('/user/:user_id/info', {templateUrl: urls.part + '/userInfo.html', controller: 'UserInfoCtrl', title: '个人信息'});
        $routeProvider.when('/user/modify', {templateUrl: urls.part + '/userModifyInfo.html', controller: 'UserModifyInfoCtrl', title: '修改个人信息'});
        $routeProvider.when('/user/password', {templateUrl: urls.part + '/userModifyPass.html', controller: 'UserModifyPassCtrl', title: '修改密码'});
        $routeProvider.when('/user/actlist', {templateUrl: urls.part + '/activityList.html', controller: 'UserActListCtrl', title: '活动列表'});
        $routeProvider.when('/user/message', {templateUrl: urls.part + '/message.html', controller: 'UserMsgCtrl', title: '站内信'});
        $routeProvider.when('/user/:search_id/search', {templateUrl: urls.part + '/searchResult.html', controller: 'UserSearchCtrl', title: '搜索结果'});
        $routeProvider.when('/act/create', {templateUrl: urls.part + '/createActivity.html', controller: 'ActivityCreateCtrl', title: '创建活动'});
        $routeProvider.when('/act/:act_id/info', {templateUrl: urls.part + '/activityInfo.html', controller: 'ActivityInfoCtrl', title: '活动信息'});
        $routeProvider.when('/act/:act_id/manage', {templateUrl: urls.part + '/modifyActivityInfo.html', controller: 'ActivityManageCtrl', title: "活动管理"});
        $routeProvider.when('/act/:act_id/user', {templateUrl: urls.part + '/verifyActivityUser.html', controller: 'ActivityUserCtrl', title: "人员管理"});
        $routeProvider.when('/user/test', {templateUrl: urls.part + '/verifyActivityUser.html', controller: 'TestCtrl', title: "人员管理"});
        $routeProvider.when('/user/:act_id/terminal', {templateUrl: urls.part + '/verifyActivityUser.html', controller: 'TurnCtrl', title: "人员管理"});
        
        $routeProvider.otherwise({redirectTo: '/'});
    }]).
    run(['$location', '$rootScope', 'urls', function($location, $rootScope, urls){
        //Configure header title of the page
        $rootScope.urls = urls;
        $rootScope.$on('$routeChangeSuccess', function(event, current, previous){
            $rootScope.title = current.$$route.title;
        });
    }]);
