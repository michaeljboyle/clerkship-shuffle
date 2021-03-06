$(function() {

  var backendHostUrl = 'https://clerkship-shuffle.appspot.com';//'http://localhost:8080'; //

  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCLEe9beHx4ryEAMv62-qPrV8M5z9A0KRQ",
    authDomain: "clerkship-shuffle.firebaseapp.com",
    databaseURL: "https://clerkship-shuffle.firebaseio.com",
    storageBucket: "clerkship-shuffle.appspot.com",
    messagingSenderId: "238402570816"
  };

  // This is passed into the backend to authenticate the user.
  window.userIdToken = null;

  // Firebase log-in widget
  function configureFirebaseLoginWidget() {
    var uiConfig = {
      'signInSuccessUrl': '/',
      'signInOptions': [
        // Leave the lines as is for the providers you want to offer your users.
        firebase.auth.EmailAuthProvider.PROVIDER_ID
      ]
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }

  var model = {
    save: function(data, block) {
      $.ajax({
        headers: {
          'Authorization': 'Bearer ' + window.userIdToken
        },
        url: backendHostUrl + '/register',
        type: 'POST',
        data: data,
        success: function(response) {
          ctrl.updateForm(response.data);
        },
        error: function(xhr, status, msg) {
          ctrl.updateFailure(block, 'Unable to save trade');
        }
      });
    },
    load: function() {
      $.ajax({
        headers: {
          'Authorization': 'Bearer ' + window.userIdToken
        },
        url: backendHostUrl + '/load',
        type: 'GET',
        success: function(response) {
          console.log(response);
          ctrl.load(response.data);
        }
      });
    }
  };

  var ctrl = {
    init: function() {
      view.init();
      model.load();
    },
    save: function(data, block) {
      model.save(data, block);
    },
    updateForm: function(data) {
      console.log('updating ' + data.block);
      view.updateBlock(data);
    },
    updateFailure: function(block, msg) {
      view.resetSubmit(block);
      view.alert(msg);
    },
    load: function(data) {
      for (var block in data) {
        ctrl.updateForm(data[block])
      }
    }
  };

  var view = {
    init: function() {
      $('button').click(function() {
        var block = $(this).attr('id').split('-')[1];
        var data = $('form#' + block).serialize();
        console.log('id is ' + block);
        console.log('data is ' + data);
        var button = $('#submit-' + block);
        button.attr('disabled', true);
        button.text('Saving...');
        ctrl.save(data, block);
      });
    },
    updateBlock: function(data) {
      var form = $('form#' + data.block);
      form.find('input[name="key"]').val(data.key);
      /*
      form.find('input[name="Current"][value="' + data.current + '"]').attr('checked', 'checked');
      form.find('input[name="Desired"][value="' + data.desired + '"]').attr('checked', 'checked');
      */
      var currentFor = data.block + '-Current-' + data.current;
      var currentInput = form.find('label[for="' + currentFor + '"]');
      currentInput.addClass('is-checked');
      currentInput.find('input').attr('checked', 'checked');
      var desiredFor = data.block + '-Desired-' + data.desired;
      var desiredInput = form.find('label[for="' + desiredFor + '"]');
      desiredInput.addClass('is-checked');
      desiredInput.find('input').attr('checked', 'checked');
      var button = $('#submit-' + data.block);
      console.log(button);
      button.removeClass('mdl-button--accent');
      button.addClass('mdl-button--colored');
      button.attr('disabled', false);
      button.text('Update Trade');
    },
    resetSubmit: function(block) {
      var form = $('form#' + block);
      var key = form.find('input[name="key"]').val();
      var button = $('#submit-' + block);
      var buttonText = 'Submit Trade';
      if (key.length > 0) {
        buttonText = 'Update Trade';
        button.removeClass('mdl-button--accent');
        button.addClass('mdl-button--colored');
      }
      button.text(buttonText);
      button.attr('disabled', false);
    },
    alert: function(msg) {
      window.alert(msg);

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
          ctrl.init();

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

  configureFirebaseLogin();
  configureFirebaseLoginWidget();
});

