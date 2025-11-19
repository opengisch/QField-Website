// Simple test to verify script is running
console.log('Main.js script loaded at:', new Date().toISOString())

let isInitialized = false
let initAttempts = 0

function initializeApp() {
  initAttempts++
  console.log(`Initialization attempt #${initAttempts}, readyState: ${document.readyState}`)
  
  if (isInitialized) {
    console.log('App already initialized, skipping')
    return
  }
  
  // Check if we have the required elements before initializing
  const testFiltersContainer = document.querySelector('[data-success-stories-filters]')
  const testCards = document.querySelectorAll('.success-story-card')
  
  if (testFiltersContainer && testCards.length === 0) {
    console.log('Filter container found but no cards yet, will retry...')
    if (initAttempts < 10) {  // Limit retry attempts
      setTimeout(initializeApp, 100)
      return
    }
  }
  
  console.log('Initializing app, readyState:', document.readyState, 'at:', new Date().toISOString())
  isInitialized = true
  
  // Initialize Bootstrap tooltips if Bootstrap is available
  if (typeof bootstrap !== 'undefined') {
    const tooltipTriggerElements = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    tooltipTriggerElements.forEach((triggerEl) => {
      new bootstrap.Tooltip(triggerEl)
    })
  }
  
  // Enhanced Sticky Navbar
  const navbar = document.querySelector('.navbar.sticky-top')
  if (navbar) {
    let lastScrollY = window.scrollY
    let isScrolled = false

    const handleScroll = () => {
      const currentScrollY = window.scrollY
      
      // Add scrolled class after scrolling down 10px
      if (currentScrollY > 10 && !isScrolled) {
        navbar.classList.add('scrolled')
        isScrolled = true
      } else if (currentScrollY <= 10 && isScrolled) {
        navbar.classList.remove('scrolled')
        isScrolled = false
      }

      lastScrollY = currentScrollY
    }

    // Throttle scroll events for better performance
    let ticking = false
    const scrollHandler = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          handleScroll()
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('scroll', scrollHandler, { passive: true })
  }

  // Customer logos functionality
  const customers = document.getElementById('customers')
  if (customers) {
    customers.querySelectorAll('.customer-logos img').forEach((img) => {
      img.addEventListener('click', () => {
        const targets = customers.querySelectorAll(`*[title="${img.title}"]`)
        targets.forEach((el) => {
          Array.from(el.parentElement.children).forEach((sibling) => sibling.classList.remove('customer-active'))
          el.classList.add('customer-active')
        })
      })
    })
  }

  // Initialize galleries with a small delay to ensure all content is loaded
  setTimeout(initializeGalleries, 100)

  // Partner region filter controls
  const regionFiltersContainer = document.getElementById('region-filters')
  if (regionFiltersContainer) {
    const filterLinks = regionFiltersContainer.querySelectorAll('a[data-region]')
    const partnerPanels = document.querySelectorAll('.panel[data-region]')
    
    console.log('Partner region filter initialized:', { 
      filterLinks: filterLinks.length, 
      panels: partnerPanels.length 
    })

    const applyRegionFilter = (region) => {
      console.log('Applying region filter:', region)

      // Update active state on nav pills (Bootstrap 5 style)
      filterLinks.forEach((link) => {
        if (link.dataset.region === region) {
          link.classList.add('active')
        } else {
          link.classList.remove('active')
        }
      })

      // Show/hide partner panels based on region
      let visibleCount = 0
      partnerPanels.forEach((panel) => {
        const regions = (panel.dataset.region || '').split(/\s+/).filter(Boolean)
        const isVisible = region === 'world' || regions.includes(region)
        
        // Toggle visibility on the parent column
        const column = panel.closest('.col-sm-6, .col-md-4')
        if (column) {
          column.classList.toggle('d-none', !isVisible)
          if (isVisible) visibleCount++
        }
      })
      
      console.log('Region filter applied:', { region, visiblePanels: visibleCount })
    }

    // Set initial filter to 'world' (show all)
    applyRegionFilter('world')

    // Add click handlers to filter links
    filterLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault()
        const region = link.dataset.region
        console.log('Region filter clicked:', region)
        applyRegionFilter(region)
      })
    })
  }

  // Success stories filter controls
  const filtersContainer = document.querySelector('[data-success-stories-filters]')
  console.log('Looking for filter container:', filtersContainer)
  
  // Manual test - add a global function for debugging
  window.testFilter = function(filterName) {
    const cards = document.querySelectorAll('.success-story-card')
    console.log('Manual test - found cards:', cards.length)
    cards.forEach((card, index) => {
      const categories = (card.dataset.categories || '').split(/\s+/).filter(Boolean)
      const isVisible = filterName === 'all' || categories.includes(filterName)
      card.classList.toggle('d-none', !isVisible)
      console.log(`Card ${index}:`, { categories: card.dataset.categories, visible: isVisible })
    })
  }
  
  if (filtersContainer) {
    const filterButtons = filtersContainer.querySelectorAll('button[data-filter]')
    const cards = document.querySelectorAll('.success-story-card')
    
    console.log('Filter system initialized:', { 
      filterButtons: filterButtons.length, 
      cards: cards.length 
    })
    
    // Test if the first card has the expected data
    if (cards.length > 0) {
      console.log('First card data-categories:', cards[0].dataset.categories)
    }

    const applyFilter = (filter) => {
      const supportedFilters = Array.from(filterButtons).map((button) => button.dataset.filter)
      const normalizedFilter = supportedFilters.includes(filter) ? filter : 'all'
      
      console.log('Applying filter:', { filter, normalizedFilter, supportedFilters })

      filterButtons.forEach((button) => {
        const isActive = button.dataset.filter === normalizedFilter
        button.classList.toggle('active', isActive)
        button.setAttribute('aria-pressed', isActive ? 'true' : 'false')
      })

      let visibleCount = 0
      cards.forEach((card) => {
        const categories = (card.dataset.categories || '').split(/\s+/).filter(Boolean)
        const isVisible = normalizedFilter === 'all' || categories.includes(normalizedFilter)
        card.classList.toggle('d-none', !isVisible)
        if (isVisible) visibleCount++
        
        if (!isVisible && normalizedFilter !== 'all') {
          console.log('Hiding card:', { 
            categories: card.dataset.categories, 
            parsed: categories, 
            filter: normalizedFilter,
            includes: categories.includes(normalizedFilter)
          })
        }
      })
      
      console.log('Filter applied:', { filter: normalizedFilter, visibleCards: visibleCount })
    }

    const urlParams = new URLSearchParams(window.location.search)
    const initialFilter = urlParams.get('filter') || 'all'
    applyFilter(initialFilter)

    filterButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        console.log('Filter button clicked:', button.dataset.filter)
        const filter = button.getAttribute('data-filter')
        const nextUrl = `${window.location.pathname}?filter=${encodeURIComponent(filter)}`
        if (window.history && history.pushState) {
          history.pushState({ filter }, '', nextUrl)
        }
        applyFilter(filter)
      })
    })

    window.addEventListener('popstate', (event) => {
      const filter = event.state?.filter || 'all'
      applyFilter(filter)
    })
  }
}

// Reset initialization on page navigation (for SPAs or cached pages)
if ('addEventListener' in window) {
  window.addEventListener('beforeunload', () => {
    isInitialized = false
    initAttempts = 0
  })
}

// Multiple initialization strategies for different loading scenarios
function tryInitialization() {
  console.log('Trying initialization, readyState:', document.readyState)
  
  // Strategy 1: DOM ready check
  if (document.readyState === 'loading') {
    console.log('Document still loading, adding DOMContentLoaded listener')
    document.addEventListener('DOMContentLoaded', initializeApp, { once: true })
  } else {
    // DOM is already ready, initialize immediately
    console.log('Document already loaded, initializing immediately')
    initializeApp()
  }
  
  // Strategy 2: Window load backup
  window.addEventListener('load', () => {
    console.log('Window load event fired')
    if (!isInitialized) {
      console.log('Not yet initialized, trying now')
      initializeApp()
    }
  }, { once: true })
  
  // Strategy 3: Delayed backup for cached pages
  setTimeout(() => {
    if (!isInitialized) {
      console.log('Delayed backup initialization')
      initializeApp()
    }
  }, 250)
}

// Gallery initialization function
function initializeGalleries() {
  const galleryWrappers = document.querySelectorAll('.gallery-wrapper[data-gallery-id]')
  console.log('Initializing galleries:', galleryWrappers.length)
  
  // Log all gallery IDs found
  galleryWrappers.forEach((wrapper, index) => {
    console.log(`Found gallery ${index + 1}:`, wrapper.dataset.galleryId)
  })
  
  if (galleryWrappers.length === 0) {
    console.log('No gallery wrappers found, will retry in 100ms')
    setTimeout(initializeGalleries, 100)
    return
  }
  
  galleryWrappers.forEach(galleryWrapper => {
    const galleryId = galleryWrapper.dataset.galleryId
    const autoplay = galleryWrapper.dataset.autoplay === 'true'
    const interval = galleryWrapper.dataset.interval || '5000'
    const controls = galleryWrapper.dataset.controls !== 'false'
    const indicators = galleryWrapper.dataset.indicators !== 'false'
    
    console.log(`Processing gallery ${galleryId}`)
    
    const figures = galleryWrapper.querySelectorAll('figure')
    console.log(`Gallery ${galleryId} found ${figures.length} figures`)
    
    if (figures.length === 0) {
      console.log(`Gallery ${galleryId} has no figures, hiding wrapper`)
      galleryWrapper.style.display = 'none'
      return
    }
    
    // Create carousel structure
    const carousel = document.createElement('div')
    carousel.id = galleryId
    carousel.className = 'carousel slide gallery-carousel mb-4'
    if (autoplay) {
      carousel.setAttribute('data-bs-ride', 'carousel')
    }
    carousel.setAttribute('data-bs-interval', interval)
    
    let carouselHTML = ''
    
    // Add indicators if more than one figure and enabled
    if (indicators && figures.length > 1) {
      carouselHTML += '<div class="carousel-indicators">'
      for (let i = 0; i < figures.length; i++) {
        carouselHTML += `<button type="button" data-bs-target="#${galleryId}" data-bs-slide-to="${i}" 
                         ${i === 0 ? 'class="active" aria-current="true"' : ''} 
                         aria-label="Slide ${i + 1}"></button>`
      }
      carouselHTML += '</div>'
    }
    
    // Add carousel inner
    carouselHTML += '<div class="carousel-inner">'
    figures.forEach((figure, index) => {
      carouselHTML += `<div class="carousel-item${index === 0 ? ' active' : ''}">`
      carouselHTML += figure.outerHTML
      carouselHTML += '</div>'
    })
    carouselHTML += '</div>'
    
    // Add controls if more than one figure and enabled
    if (controls && figures.length > 1) {
      carouselHTML += `
        <button class="carousel-control-prev" type="button" data-bs-target="#${galleryId}" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#${galleryId}" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Next</span>
        </button>
      `
    }
    
    carousel.innerHTML = carouselHTML
    
    // Replace the wrapper with the carousel
    galleryWrapper.parentNode.replaceChild(carousel, galleryWrapper)
    
    // Initialize Bootstrap carousel
    if (typeof bootstrap !== 'undefined' && bootstrap.Carousel) {
      try {
        new bootstrap.Carousel(carousel, {
          interval: parseInt(interval),
          ride: autoplay ? 'carousel' : false,
          pause: 'hover',
          wrap: true,
          keyboard: true,
          touch: true
        })
        console.log(`Gallery ${galleryId} Bootstrap carousel initialized`)
      } catch (error) {
        console.error(`Failed to initialize Bootstrap carousel for ${galleryId}:`, error)
      }
    } else {
      console.warn('Bootstrap not available for carousel initialization')
    }
    
    console.log(`Gallery ${galleryId} initialized successfully with ${figures.length} slides`)
  })
}

// Start initialization
tryInitialization()
