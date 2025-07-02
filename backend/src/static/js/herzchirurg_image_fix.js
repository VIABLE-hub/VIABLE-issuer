// 🩺 HERZCHIRURG IMAGE SAFETY MODULE
// Prevents black/empty images during QR code generation

console.log("🩺 HERZCHIRURG: Image Safety Module Loading...");

// Image validation function
function validateImageSrc(src) {
  if (!src || src === "" || src.includes("black") || src === "about:blank") {
    return false;
  }
  // Check for problematic base64 patterns (specific truncated version)
  if (src.includes("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSrcgSlBFRyB2ODApLCBxdWFsaXR5ID0gODUK/9sAQwAGBAUGBQQGBgUGBwcGCAoQCgoJCQoUDg0NDhQUExMTExQU")) {
    return false;
  }
  return true;
}

// Safe image source getter with fallback
function getSafeImageSrc(currentSrc, fallbackSrc) {
  if (validateImageSrc(currentSrc)) {
    return currentSrc;
  }
  console.log("🩺 HERZCHIRURG: Using fallback image due to invalid current src");
  return fallbackSrc;
}

// Setup safety handlers for images
function setupImageSafetyHandlers() {
  console.log("🩺 HERZCHIRURG: Setting up image safety handlers");
  
  // Profile image safety
  const imagePreview = document.getElementById('imagePreview');
  if (imagePreview) {
    // Add error handler
    imagePreview.onerror = function() {
      console.log("🩺 HERZCHIRURG: Profile image load error, using fallback");
      this.src = '/static/student.png';
      this.onerror = null; // Prevent infinite loop
    };
    
    // Validate current src on page load
    const currentSrc = imagePreview.src;
    if (!validateImageSrc(currentSrc)) {
      console.log("🩺 HERZCHIRURG: Invalid profile image detected, using fallback");
      imagePreview.src = '/static/student.png';
    }
    
    console.log("🩺 HERZCHIRURG: Profile image safety handlers installed");
  }

  // Theme icon safety
  const themeIconPreview = document.getElementById('themeIconPreview');
  if (themeIconPreview) {
    // Add error handler
    themeIconPreview.onerror = function() {
      console.log("🩺 HERZCHIRURG: Theme icon load error, using fallback");
      this.src = '/static/studentVC-logo-sora-cropped-darkmode.png';
      this.onerror = null; // Prevent infinite loop
    };
    
    // Validate current src on page load
    const currentSrc = themeIconPreview.src;
    if (!validateImageSrc(currentSrc)) {
      console.log("🩺 HERZCHIRURG: Invalid theme icon detected, using fallback");
      themeIconPreview.src = '/static/studentVC-logo-sora-cropped-darkmode.png';
    }
    
    console.log("🩺 HERZCHIRURG: Theme icon safety handlers installed");
  }
}

// Enhanced reset function with safety checks
function safeResetProfileImage() {
  const imagePreview = document.getElementById('imagePreview');
  const profileImageInput = document.getElementById('profileImage');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const dropZone = document.getElementById('dropZone');
  
  if (imagePreview) {
    // Use safe fallback
    const safeSrc = getSafeImageSrc('/static/student.png', '/static/student.png');
    imagePreview.src = safeSrc;
    
    // Add safety handler
    imagePreview.onerror = function() {
      console.log("🩺 HERZCHIRURG: Reset image load error, using absolute fallback");
      this.src = '/static/student.png';
      this.onerror = null;
    };
    
    console.log("🩺 HERZCHIRURG: Profile image safely reset");
  }
  
  if (profileImageInput) {
    profileImageInput.value = '';
  }
  
  // Reset visual states
  if (imagePreviewContainer) {
    imagePreviewContainer.classList.remove('ring-2', 'ring-berlin-blue');
  }
  
  if (dropZone) {
    dropZone.classList.remove('border-berlin-blue', 'bg-blue-50');
    dropZone.classList.add('border-dashed');
  }
}

// Enhanced reset function for theme icon
function safeResetThemeIcon() {
  const themeIconPreview = document.getElementById('themeIconPreview');
  const themeIconInput = document.getElementById('theme_icon');
  const themeIconPreviewContainer = document.getElementById('themeIconPreviewContainer');
  const themeDropZone = document.getElementById('themeDropZone');
  
  if (themeIconPreview) {
    // Use safe fallback
    const safeSrc = getSafeImageSrc('/static/studentVC-logo-sora-cropped-darkmode.png', '/static/studentVC-logo-sora-cropped-darkmode.png');
    themeIconPreview.src = safeSrc;
    
    // Add safety handler
    themeIconPreview.onerror = function() {
      console.log("🩺 HERZCHIRURG: Reset theme icon load error, using absolute fallback");
      this.src = '/static/studentVC-logo-sora-cropped-darkmode.png';
      this.onerror = null;
    };
    
    console.log("🩺 HERZCHIRURG: Theme icon safely reset");
  }
  
  if (themeIconInput) {
    themeIconInput.value = '';
  }
  
  // Reset visual states
  if (themeIconPreviewContainer) {
    themeIconPreviewContainer.classList.remove('ring-2', 'ring-berlin-blue');
  }
  
  if (themeDropZone) {
    themeDropZone.classList.remove('border-berlin-blue', 'bg-blue-50');
    themeDropZone.classList.add('border-dashed');
  }
}

// Validation for uploaded files
function validateAndPreviewImage(file, previewElement, containerElement, dropZoneElement) {
  if (!file || !previewElement) {
    console.warn("🩺 HERZCHIRURG: Invalid file or preview element");
    return false;
  }
  
  // Check file type
  if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
    alert("Bitte nur JPG oder PNG Bilder hochladen.");
    return false;
  }
  
  // Check file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert("Datei ist zu groß. Bitte wählen Sie ein Bild unter 5MB.");
    return false;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const result = e.target.result;
    if (validateImageSrc(result)) {
      previewElement.src = result;
      
      // Add visual feedback
      if (containerElement) {
        containerElement.classList.add('ring-2', 'ring-berlin-blue');
      }
      if (dropZoneElement) {
        dropZoneElement.classList.add('border-berlin-blue', 'bg-blue-50');
        dropZoneElement.classList.remove('border-dashed');
      }
      
      console.log("🩺 HERZCHIRURG: Successfully loaded safe image preview");
      return true;
    } else {
      console.warn("🩺 HERZCHIRURG: Uploaded image failed validation");
      alert("Das hochgeladene Bild scheint beschädigt zu sein. Bitte versuchen Sie es mit einem anderen Bild.");
      return false;
    }
  };
  
  reader.onerror = function() {
    console.error("🩺 HERZCHIRURG: FileReader error occurred");
    alert("Fehler beim Laden des Bildes. Bitte versuchen Sie es erneut.");
    return false;
  };
  
  reader.readAsDataURL(file);
  return true;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  console.log("🩺 HERZCHIRURG: Image Safety Module initializing...");
  
  // Set up safety handlers
  setupImageSafetyHandlers();
  
  // Override reset button handlers
  const resetImageBtn = document.getElementById('resetImageBtn');
  if (resetImageBtn) {
    resetImageBtn.addEventListener('click', function(e) {
      e.preventDefault();
      safeResetProfileImage();
      return false;
    });
    console.log("🩺 HERZCHIRURG: Profile reset button handler installed");
  }
  
  const resetThemeIconBtn = document.getElementById('resetThemeIconBtn');
  if (resetThemeIconBtn) {
    resetThemeIconBtn.addEventListener('click', function(e) {
      e.preventDefault();
      safeResetThemeIcon();
      return false;
    });
    console.log("🩺 HERZCHIRURG: Theme icon reset button handler installed");
  }
  
  // Monitor for dynamic image changes (e.g., after form submission)
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'attributes' && mutation.attributeName === 'src') {
        const target = mutation.target;
        if (target.id === 'imagePreview' || target.id === 'themeIconPreview') {
          if (!validateImageSrc(target.src)) {
            console.log("🩺 HERZCHIRURG: Invalid image detected via mutation observer, fixing...");
            if (target.id === 'imagePreview') {
              target.src = '/static/student.png';
            } else if (target.id === 'themeIconPreview') {
              target.src = '/static/studentVC-logo-sora-cropped-darkmode.png';
            }
          }
        }
      }
    });
  });
  
  // Observe image elements for changes
  const imagePreview = document.getElementById('imagePreview');
  const themeIconPreview = document.getElementById('themeIconPreview');
  
  if (imagePreview) {
    observer.observe(imagePreview, { attributes: true, attributeFilter: ['src'] });
  }
  
  if (themeIconPreview) {
    observer.observe(themeIconPreview, { attributes: true, attributeFilter: ['src'] });
  }
  
  console.log("🩺 HERZCHIRURG: Image Safety Module fully initialized ✅");
});

// Global functions for external access
window.herzchirurgValidateImageSrc = validateImageSrc;
window.herzchirurgSafeResetProfileImage = safeResetProfileImage;
window.herzchirurgSafeResetThemeIcon = safeResetThemeIcon;

console.log("🩺 HERZCHIRURG: Image Safety Module loaded ✅"); 