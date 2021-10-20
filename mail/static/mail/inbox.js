(function () {
  'use strict'
var errorMsg = document.querySelector('#error_msg');
//var csrftoken = "";
document.addEventListener('DOMContentLoaded', function () {

  // form validation
  FormValidation()

  // csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  var form = document.getElementById("compose-form");
  form.reset()
  form.onsubmit = tosubmit;
  
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  var emailsview = document.querySelector('#emails-view');
  emailsview.style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  emailsview.innerHTML = "";
 
  Getter("/emails/" + mailbox)  
    .then(emails => { 
      emailsview.insertAdjacentHTML("beforeend", "<h4 class='text-capitalize'>" + mailbox +': '+ emails.length+ "</h4> ");

      emails.forEach(email => {
      
        const link = "emails/" + email.id;
        const bg = email.read === true ? "bg-light" : "bg-info";
        console.log(email)
        emailsview.insertAdjacentHTML("beforeend", "<div class='media media-body position-relative msg " + bg + "' > <a class='email btn btn-default stretched-link strong'  read='" + email.read + "'  href=" + link + " > " + email.sender + " : </a> <strong> " + email.subject + "</strong>    " + email.timestamp + " </div><br>")
      });

      // ... do something else with email ...
      reademail()
    })
  function reademail() {

    //read emails
    document.querySelectorAll(".email").forEach(function (elm) {

      elm.onclick = (e) => {

        e.preventDefault()
        const ee = e.target;

        if (mailbox === "inbox" && ee.getAttribute("read") === 'false') {
          Postman("PUT", ee.href, { read: true })
        }

        // then get call
        Getter(ee.href).then(email => {
          let link = "emails/" + email.id;
          let recipient = "";
          email.recipients.forEach((s) => recipient += s + ", ");
          var archivemsg = email.archived === true ? "unarchived" : "archived";
          emailsview.innerHTML = "";
          emailsview.innerHTML = "<p class='lead'> <strong>From : </strong> " + email.sender + " <br><strong>To : </strong>" + recipient + "<br> <strong> Subject : </strong>" + email.subject + "<br> <strong>Timestamp : </strong>" + email.timestamp + "<br><a id='reply' href='#' email='" + email.sender + "' subject='" + email.subject + "' >Reply</a>  |  <a id='archive' archived=" + email.archived + " href=" + link + "  > " + archivemsg + "</a> <hr><br> " + email.body + "</p>"
          // read and archive
          sortout();
        });

      }
    })

  }

}

function sortout() {
  // sortout replies
  document.getElementById("reply").onclick = function (re) {
    re.preventDefault()
    compose_email()
    document.querySelector("#compose-recipients").value = re.target.getAttribute("email");
    document.querySelector("#compose-subject").value = "Re: " + re.target.getAttribute("subject");
  }


  // sortout archive
  document.getElementById("archive").onclick = function (e) {
    e.preventDefault()

    let ee = e.target;
    let arrv = ee.getAttribute("archived") === 'true' ? false : true

    Postman("PUT", ee.href, {
      archived: arrv
    }).then(archiveResponse => {
      load_mailbox('inbox')
    });
  }
}

function tosubmit(e) {
  e.preventDefault()
  var form = e.target;
  if (form.checkValidity() === false) {

    return false;
  }

  let elms = form.elements;

  const options = {
    recipients: elms.namedItem('compose-recipients').value,
    subject: elms.namedItem('compose-subject').value,
    body: elms.namedItem('compose-body').value,
  }

  Postman("POST", "/emails", options).then(response => {
    if (response.error){
      show_error(response.error)
    }else{
    console.log(response);
    load_mailbox('sent')
    }
  });
};

function show_error(errMsg){
  if (errMsg){
    errorMsg.classList.remove('d-none')
    errorMsg.innerHTML = errMsg
    errorMsg.classList.add('d-block')

    setTimeout(() => {
    errorMsg.classList.remove('d-block')
    errorMsg.innerHTML = ""
    errorMsg.classList.add('d-none')
    }, 5000);
  }
}

async function Getter(url) {
  return fetch(url)
    .then(response => response.json())
}

async function Postman(method, url, bodyarg) {

  const options = {
    method: method,
    mode: 'same-origin', // Do not send CSRF token to another domain.,
    body: JSON.stringify(bodyarg)
  }
  const request = new Request(
    url,
    { headers: { 'X-CSRFToken': getCsrfToken() } }
  );
  if (method === "PUT")
    return fetch(request, options)
  return fetch(request, options)
    .then(response => response.json())
}


// get cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

//const csrftoken = getCookie('csrftoken');
function getCsrfToken(){
  let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  if (!csrftoken){
    csrftoken = getCookie('csrftoken')
  }
  return csrftoken
}


//############# form validation events
function FormValidation(){
  //set validations  events
  document.querySelectorAll("input").forEach(function (elm) {
    common(elm)
    });
    
    document.querySelectorAll("textarea").forEach(function (elm) {
    common(elm)
    });
       // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          // check for password match
          if (form.id === "register" || form.id === "reset_confirm") {
                var password = form.querySelector('input[name="password"]');
                var confirm = form.querySelector('input[name="confirmation"]');
                if (password.value !== confirm.value){
                  password.setCustomValidity("Passwords Don't Match")
                  confirm.setCustomValidity("Passwords Don't Match")
                }else{
                  password.setCustomValidity("");
                  confirm.setCustomValidity("");
                } 

                checkedUp(password)
                checkedUp(confirm)
        }
          // now handle form 
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }
  
          form.classList.add('was-validated')
        }, false)
      })
}

function Reg(_type, _val) {
  switch (_type) {
      case "text":
          return /^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9 _]*$/.test(_val) ? "" : "text numbers and space only";
      case "textarea":
          return !(/[^A-Za-z0-9 .'?!,@$#-_]/).test(_val) ? "" : "text and numbers only";
      case "email":
          return /^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/.test(_val) ? "": "valid email eg: user@example.com";
      case "password":
          return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,10}/.test(_val) ? "" : "8 to 10 chars 1 uppercase lowercase number and special char";
  }
}
function checkedUp(_elm) {
  let  nx = _elm.nextElementSibling, has = nx ? nx.className.indexOf("invalid-feedback") > -1 ? true : false : false;
  if (!_elm.validity.valid) {
      if (has) {
          nx.innerHTML = _elm.validationMessage;
      } else {

        _elm.insertAdjacentHTML("afterend","<div class='invalid-feedback '>" + _elm.validationMessage + "</div>");
      }
      _elm.classList.remove('is-valid')
      _elm.classList.add('is-invalid')
      return false;
  } else {
      if (has) {
          nx.innerHTML = "";
      }
      _elm.classList.remove('is-invalid')
      _elm.classList.add('is-valid')
      return true;
  }
}
function sorted(_elm) {
  let  _type = _elm.getAttribute("type");

  if (!_type){
    return
  }else{
  _type = _type.toLowerCase()
  }

if (_elm.tagName.toLowerCase() === "textarea"){
    _type = "textarea"
}
_elm.setCustomValidity(Reg(_type, _elm.value));

  return checkedUp(_elm);
}

function common(elm){
  elm.addEventListener('change', function(e){
    if (!sorted(e.target)) {
    e.preventDefault();
    e.stopPropagation();
  }
  });
}

})()