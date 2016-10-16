$(function() {

  var backendHostUrl = 'http://localhost:8080';//'https://clerkship-shuffle.appspot.com';

  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCLEe9beHx4ryEAMv62-qPrV8M5z9A0KRQ",
    authDomain: "clerkship-shuffle.firebaseapp.com",
    databaseURL: "https://clerkship-shuffle.firebaseio.com",
    storageBucket: "clerkship-shuffle.appspot.com",
    messagingSenderId: "238402570816"
  };

  // This is passed into the backend to authenticate the user.
  userIdToken = null;

  // Firebase log-in widget
  function configureFirebaseLoginWidget() {
    var uiConfig = {
      'signInSuccessUrl': '/results',
      'signInOptions': [
        // Leave the lines as is for the providers you want to offer your users.
        firebase.auth.EmailAuthProvider.PROVIDER_ID
      ]
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }

  var model = {
    load: function() {
      $.ajax({
        headers: {
          'Authorization': 'Bearer ' + window.userIdToken
        },
        url: backendHostUrl + '/load',
        type: 'GET',
        success: function(response) {
          console.log(response);
          ctrl.update(response.data);
        }
      });
    }
  };

  var ctrl = {
    init: function() {
      view.init();
    },
    load: function() {
      model.load();
    },
    update: function(data) {
      for (var block in data) {
        view.update(data[block])
      }
    },
    map: function(input) {
      var m = {'pcpsych': 'Primary Care / Psych',
      'imneuro': 'Medicine / Neurology',
      'surgem': 'Surgery / Emergency',
      'pedobgyn': 'Pediatrics / ObGyn'};
      return m[input];
    }
  };

  var view = {
    init: function() {
      $('.block').find('.matchinfo').hide();
      $('.matchstatus').text('not found');
    },
    update: function(data) {
      var block = $('div#block' + data.block);
      var status = block.find('.matchstatus');
      var info = block.find('.matchinfo');
      var desired = block.find('.desired');
      var donor = block.find('.donor');
      var current = block.find('.current');
      var receiver = block.find('.receiver');
      if (data.match_to_current_email) {
        status.text('found!');
        info.show();
        desired.text(ctrl.map(data.desired));
        donor.text(data.match_to_desired_email);
        current.text(ctrl.map(data.current));
        receiver.text(data.match_to_current_email);
      }
      else {
        status.text('not found')
        info.hide();
      }
    }
  };

  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START onAuthStateChanged]
    firebase.auth().onAuthStateChanged(function(user) {
      console.log('auth state changed');
      if (user) {
        $('#logged-out').hide();
        var name = user.displayName;

        /* If the provider gives a display name, use the name for the
        personal welcome message. Otherwise, use the user's email. */
        var welcomeName = name ? name : user.email;

        user.getToken().then(function(idToken) {
          window.userIdToken = idToken;
          ctrl.load();

          $('#user').text(welcomeName);
          $('#logged-in').show();

        });

      } else {
        console.log('no user');
        $('#logged-in').hide();
        $('#logged-out').show();

      }
    // [END onAuthStateChanged]

    });
  }

  ctrl.init();
  configureFirebaseLogin();
  configureFirebaseLoginWidget();
});