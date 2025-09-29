// Add any JavaScript code for future functionality
// Example: Filter functionality or form validation
// Handle the filter functionality for doctors based on specialization
document.getElementById('qualification').addEventListener('change', function () {
    const selectedQualification = this.value;
    const doctorItems = document.querySelectorAll('.doctor-item');
  
    doctorItems.forEach(function (item) {
      const qualification = item.getAttribute('data-specialization');
      if (selectedQualification === 'All' || qualification === selectedQualification) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  });
  
  // Basic form validation for registration and login pages
  const validateForm = (form) => {
    const inputs = form.querySelectorAll('input');
    for (let i = 0; i < inputs.length; i++) {
      if (!inputs[i].value.trim()) {
        alert(`${inputs[i].placeholder} is required!`);
        return false;
      }
    }
    return true;
  };
  
  // Handle registration form validation
  const patientForm = document.querySelector('.patient-form');
  if (patientForm) {
    patientForm.addEventListener('submit', function (event) {
      if (!validateForm(patientForm)) {
        event.preventDefault();
      }
    });
  }
  
  // Handle doctor registration form validation
  const doctorForm = document.querySelector('.doctor-form');
  if (doctorForm) {
    doctorForm.addEventListener('submit', function (event) {
      if (!validateForm(doctorForm)) {
        event.preventDefault();
      }
    });
  }
  
  // Handle login form validation
  const loginForm = document.querySelector('.login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      if (!validateForm(loginForm)) {
        event.preventDefault();
      }
    });
  }
  