window.PAMPANITO_TOUR_MEDIA = {
  // Optional: replace the audio track for a compartment with a movie.
  // If left null, pampanito.html will automatically try these files in /web/videos/:
  //   Flat files:
  //     <compartment>-mobile.mp4/.mov/.m4v/.webm
  //     <compartment>-desktop.mp4/.mov/.m4v/.webm
  //     <compartment>.mp4/.mov/.m4v/.webm
  //   Per-compartment folders:
  //     <compartment>/mobile.mp4/.mov/.m4v/.webm
  //     <compartment>/desktop.mp4/.mov/.m4v/.webm
  //     <compartment>/<compartment>-mobile.mp4/.mov/.m4v/.webm
  //     <compartment>/<compartment>-desktop.mp4/.mov/.m4v/.webm
  //     <compartment>/<compartment>.mp4/.mov/.m4v/.webm
  //     <compartment>/tour.mp4/.mov/.m4v/.webm
  // Example automatic filenames:
  //   after_deck-mobile.mp4
  //   after_deck-desktop.mp4
  //   control_room-desktop.mov
  //   conning_tower-mobile.m4v
  //
  // Set an explicit object only when you want to override the default filename,
  // poster, or title/caption.
  // Example:
  // after_deck: {
  //   type: 'video',
  //   mobileSrc: '/web/videos/after_deck-mobile.mp4',
  //   desktopSrc: '/web/videos/after_deck-desktop.mp4',
  //   poster: '/web/images/USS_Pampanito 2560x1440.jpg',
  //   title: 'After Deck Movie',
  //   caption: 'Exterior walkthrough video for the after deck.'
  // }
  trackPlaybackMedia: {
    after_deck: {
      type: 'video',
      src: '/web/videos/after_deck.mp4',
      title: 'After Deck Video Tour',
      caption: 'Aft deck video tour.'
    },
    after_torpedo_room: {
      type: 'video',
      file: 'after_torpedo.mp4',
      title: 'After Torpedo Room Video Tour',
      caption: 'After torpedo room video tour.'
    },
    maneuvering_room: null,
    after_engine_room: null,
    forward_engine_room: null,
    after_battery: null,
    crews_mess: null,
    radio_room: null,
    control_room: null,
    conning_tower: null,
    forward_battery_compartment: {
      type: 'video',
      file: 'forward_battery.mp4',
      title: 'Forward Battery Video Tour',
      caption: 'Forward battery compartment video tour.'
    },
    forward_torpedo_room: null,
    forward_deck: null
  },

  defaultVisual: {
    src: '/web/images/USS_Pampanito 2560x1440.jpg',
    alt: 'USS Pampanito underway',
    title: 'USS Pampanito (SS-383)',
    caption: 'Timed images for each stop appear here as the tour audio reaches key moments.'
  },

  trackVisualDefaults: {
    after_deck: {
      src: '/web/images/USS_Pampanito 2560x1440.jpg',
      alt: 'USS Pampanito underway',
      title: 'After Deck',
      caption: 'Aft deck visuals can introduce the boat, her wartime setting, and exterior features.'
    },
    after_torpedo_room: {
      src: '/web/images/USS-Pampanito 2237x2237.jpg',
      alt: 'USS Pampanito',
      title: 'After Torpedo Room',
      caption: 'Add interior torpedo room images here as you collect them.'
    },
    maneuvering_room: {
      src: '/web/images/USS_Pampanito_(submarine)_2012-09-30_15-13-00.jpg',
      alt: 'USS Pampanito museum view',
      title: 'Maneuvering Room',
      caption: 'Use this stop for motor controls, gauges, or electrical control imagery.'
    },
    after_engine_room: {
      src: '/web/images/USS-Pampanito 2237x2237.jpg',
      alt: 'USS Pampanito',
      title: 'After Engine Room',
      caption: 'Add diesel engine and machinery visuals for the after engine room.'
    },
    forward_engine_room: {
      src: '/web/images/USS-Pampanito 2237x2237.jpg',
      alt: 'USS Pampanito',
      title: 'Forward Engine Room',
      caption: 'Add forward engine room images and equipment close-ups here.'
    },
    after_battery: {
      src: '/web/images/USS_Pampanito_(submarine)_2012-09-30_15-13-00.jpg',
      alt: 'USS Pampanito museum view',
      title: 'After Battery',
      caption: 'Use this stop for bunks, battery well, and crew living-space images.'
    },
    crews_mess: {
      src: '/web/images/USS_Pampanito_(submarine)_2012-09-30_15-13-00.jpg',
      alt: 'USS Pampanito museum view',
      title: "Crew's Mess",
      caption: 'Add galley, mess tables, food storage, and daily-life visuals here.'
    },
    radio_room: {
      src: '/web/images/USS_Pampanito_(submarine)_2012-09-30_15-13-00.jpg',
      alt: 'USS Pampanito museum view',
      title: 'Radio Room',
      caption: 'Use this stop for communications gear, code work, and radio equipment images.'
    },
    control_room: {
      src: '/web/images/USS_Pampanito_(submarine)_2012-09-30_15-13-00.jpg',
      alt: 'USS Pampanito museum view',
      title: 'Control Room',
      caption: 'Add diving controls, helm, gauges, and central operating space visuals here.'
    },
    conning_tower: {
      src: '/web/images/pampanito conning tower.jpg',
      alt: 'USS Pampanito conning tower',
      title: 'Conning Tower',
      caption: 'This stop highlights the compact command position from which the boat fought and navigated.'
    },
    forward_battery_compartment: {
      src: '/web/images/USS_Pampanito_(submarine)_2012-09-30_15-13-00.jpg',
      alt: 'USS Pampanito museum view',
      title: 'Forward Battery',
      caption: 'Add battery, bunks, and crew-space visuals for the forward battery compartment.'
    },
    forward_torpedo_room: {
      src: '/web/images/USS-Pampanito 2237x2237.jpg',
      alt: 'USS Pampanito',
      title: 'Forward Torpedo Room',
      caption: 'Use this stop for torpedo tubes, reloads, bunks, and loading gear.'
    },
    forward_deck: {
      src: '/web/images/USS_Pampanito 2560x1440.jpg',
      alt: 'USS Pampanito underway',
      title: 'Forward Deck',
      caption: 'Add bow, deck gun, fairwater, or topside views for the forward deck stop.'
    }
  },

  trackImageCues: {
    after_deck: [
      {
        time: '0:00',
        src: '/web/images/tour/aft deck/Japanese_aircraft_attacking_Pearl_Harbor,_1941.jpg',
        alt: 'Japanese aircraft attacking Pearl Harbor in 1941',
        title: 'Pearl Harbor',
        caption: 'The attack on Pearl Harbor frames the wartime world that boats like Pampanito entered.'
      },
      {
        time: '0:18',
        src: '/web/images/tour/aft deck/President_Franklin_D._Roosevelt-1941.jpg',
        alt: 'President Franklin D. Roosevelt in 1941',
        title: 'President Franklin D. Roosevelt',
        caption: 'Roosevelt led the United States through mobilization as the submarine campaign expanded.'
      },
      {
        time: '0:42',
        src: '/web/images/tour/aft deck/Edward_L.Beach_1960.jpg',
        alt: 'Edward L. Beach in 1960',
        title: 'Edward L. Beach',
        caption: 'Submariner and author Edward L. Beach helped define how later generations understood submarine service.'
      }
    ],
    after_torpedo_room: [],
    maneuvering_room: [],
    after_engine_room: [],
    forward_engine_room: [],
    after_battery: [],
    crews_mess: [],
    radio_room: [],
    control_room: [],
    conning_tower: [],
    forward_battery_compartment: [],
    forward_torpedo_room: [],
    forward_deck: []
  }
};