document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("bgVideo");
    const loader = document.getElementById("loader");
    const scroller = document.getElementById("scroller");
  
    // HUD Panels
    const panelIntro = document.getElementById("panelIntro");
    const panelProjects = document.getElementById("panelProjects");
    const panelSkills = document.getElementById("panelSkills");
    const panelContact = document.getElementById("panelContact");
  
    // Project Cards for the "Walking/Pop" effect
    const projSteps = [
      document.getElementById("proj1"),
      document.getElementById("proj2"),
      document.getElementById("proj3"),
      document.getElementById("proj4")
    ];
  
    // Variables
    let videoDuration = 0;
    // We want the scroll length to be proportional to video length.
    // E.g. 500 pixels scrolled = 1 second of video.
    const pixelsPerSecond = 800; 
  
    video.addEventListener("loadedmetadata", () => {
      videoDuration = video.duration;
      // Set the height of the scroller body based on exact video length
      scroller.style.height = `${videoDuration * pixelsPerSecond}px`;
      
      // Hide loader to indicate video is ready
      loader.style.opacity = 0;
      setTimeout(() => loader.style.display = 'none', 1000);
      
      // Start the render loop
      requestAnimationFrame(renderLoop);
    });
  
    // Handle case where metadata is already loaded (cache)
    if (video.readyState >= 1) {
        video.dispatchEvent(new Event('loadedmetadata'));
    }
  
    // The render loop scrubs the video and manipulates the CSS elements 
    // seamlessly based on window.scrollY
    function renderLoop() {
      // Calculate how far down the user has scrolled as a percentage 0.0 -> 1.0
      // Maximum scrollable distance
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      let scrollY = window.scrollY;
      
      // Prevent negative scroll bounds in Safari
      if(scrollY < 0) scrollY = 0;
      if(scrollY > maxScroll) scrollY = maxScroll;
  
      const scrollPercent = scrollY / maxScroll;
      
      // 1. Scrub Video Time
      // Ensures the video plays forward when scrolling down, backward when scrolling up
      if(videoDuration > 0) {
          // Add a tiny bit of easing/lerp here if the video feels choppy, 
          // but direct assignment usually works fine for local mp4 files with keyframes.
          const targetTime = scrollPercent * videoDuration;
          if (Math.abs(video.currentTime - targetTime) > 0.05) {
             video.currentTime = targetTime;
          }
      }
  
      // 2. Animate HUDs based on specific percentage ranges
      updatePanels(scrollPercent);
  
      requestAnimationFrame(renderLoop);
    }
  
    // Define the distinct "Acts" in the video scene mapping to UI elements
    function updatePanels(sp) {
      // --- ACT 1: Intro Face Reveal (0% to 20%) ---
      if (sp > 0.02 && sp < 0.20) {
        const localSp = (sp - 0.02) / 0.18; // 0 to 1 inside this segment
        // Fade in rapidly, stay, then fade out
        if(localSp < 0.2) panelIntro.style.opacity = localSp * 5;
        else if(localSp > 0.8) panelIntro.style.opacity = (1 - localSp) * 5;
        else panelIntro.style.opacity = 1;
      } else {
        panelIntro.style.opacity = 0;
      }
  
      // --- ACT 2: Footsteps / Projects (20% to 55%) ---
      // We have 4 projects, stagger them as we scroll through the 35%
      if (sp > 0.20 && sp < 0.55) {
        panelProjects.style.opacity = 1;
        panelProjects.classList.add('active');
        const projRange = 0.35 / 4; // Length of each project's appearance
        
        projSteps.forEach((proj, idx) => {
            const start = 0.20 + (idx * projRange);
            const end = start + projRange;
            if (sp > start && sp < end) {
                const localSp = (sp - start) / projRange;
                
                // 3D Pop Effect: Start small/far away, move forward, fade out.
                const scale = 0.5 + (localSp * 0.7); // 0.5 -> 1.2
                const tZ = -500 + (localSp * 500); // Backwards to neutral
                
                let opacity = 1;
                if(localSp < 0.2) opacity = localSp * 5; // fade in
                if(localSp > 0.8) opacity = (1 - localSp) * 5; // fade out
                
                proj.style.opacity = opacity;
                proj.style.transform = `translate(-50%, -50%) scale(${scale}) translateZ(${tZ}px)`;
            } else {
                proj.style.opacity = 0;
            }
        });
      } else {
        panelProjects.style.opacity = 0;
        panelProjects.classList.remove('active');
        projSteps.forEach(p => p.style.opacity = 0);
      }
  
      // --- ACT 3: Skills / Hashira Ambush (55% to 80%) ---
      if (sp > 0.55 && sp < 0.80) {
        panelSkills.style.opacity = 1;
        const localSp = (sp - 0.55) / 0.25;
        // Animate skill bars filling up
        if(localSp > 0.1) {
             document.querySelector('.html-fill').style.width = '85%';
             document.querySelector('.css-fill').style.width = '82%';
             document.querySelector('.js-fill').style.width = '75%';
             document.querySelector('.py-fill').style.width = '70%';
        }
      } else {
        panelSkills.style.opacity = 0;
        // Reset bars
        document.querySelectorAll('.fill').forEach(f => f.style.width = '0%');
      }
  
      // --- ACT 4: The Turn / Contact (80% to 100%) ---
      if (sp > 0.80) {
        const localSp = (sp - 0.80) / 0.20;
        let opacity = 1;
        if(localSp < 0.3) opacity = localSp * 3.33;
        panelContact.style.opacity = opacity;
        panelContact.classList.add('active');
        
        // Minor scale up
        const scale = 0.9 + (localSp * 0.1);
        document.querySelector('.contact-box').style.transform = `scale(${scale})`;
      } else {
        panelContact.style.opacity = 0;
        panelContact.classList.remove('active');
      }
    }
  });
