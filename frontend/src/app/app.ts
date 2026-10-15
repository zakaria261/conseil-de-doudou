import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

type View = 'home' | 'coaches' | 'appointments' | 'messages' | 'community' | 'profile' | 'offers' | 'companion' | 'admin';

interface Coach {
  id: string;
  name: string;
  initials: string;
  age?: number;
  title: string;
  studies: string;
  bio: string;
  specialties: string[];
  nextSlots: string[];
  online: boolean;
  tone: string;
  photoUrl?: string;
  followed?: boolean;
}

interface Post {
  id: number;
  author: string;
  initials: string;
  time: string;
  title: string;
  body: string;
  topic: string;
  room: string;
  likes: number;
  replies: number;
  liked?: boolean;
}

interface Offer {
  id: string;
  name: string;
  description: string;
  price: number;
  unit: string;
  popular?: boolean;
  active?: boolean;
}

interface Booking {
  id: number;
  coachName: string;
  coachInitials: string;
  kind: string;
  dateTime: string;
  status: string;
}

interface ChatMessage {
  sender: string;
  text: string;
  time: string;
  own?: boolean;
}

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  constructor(private http: HttpClient) {}

  view: View = 'home';
  mobileMenuOpen = false;
  mobileSearchOpen = false;
  profileMenuOpen = false;
  showSosModal = false;
  showBookingModal = false;
  showPostComposer = false;
  isPrivateRoom = false;
  globalQuery = '';
  communityQuery = '';
  selectedTopic = 'Tout voir';
  activeThread = 'Sarah';
  notificationOn = true;
  toast = '';
  toastTimer?: ReturnType<typeof setTimeout>;
  selectedCoach?: Coach;
  selectedSlot = '';
  selectedOffer = 'message';
  postDraft = '';
  messageDraft = '';
  slotDraft = '';
  user = { pseudo: 'Dounia', bio: 'J’avance à mon rythme, un jour après l’autre.', email: 'dounia@exemple.fr' };

  readonly navItems: { id: View; label: string; icon: string }[] = [
    { id: 'home', label: 'Accueil', icon: 'home' },
    { id: 'coaches', label: 'Accompagnateurs', icon: 'sparkles' },
    { id: 'appointments', label: 'Mes rendez-vous', icon: 'calendar' },
    { id: 'messages', label: 'Messages', icon: 'message' },
    { id: 'community', label: 'Chat & partage', icon: 'heart' },
    { id: 'profile', label: 'Mon profil', icon: 'user' },
  ];

  readonly topics = ['Tout voir', 'Confiance en soi', 'Vie quotidienne', 'Relations', 'Travail'];

  coaches: Coach[] = [
    {
      id: 'hugo', name: 'Hugo', initials: 'HU', age: 23, title: 'Accompagnateur de vie',
      studies: 'Licence en psychologie · Sorbonne · Formation en psychologie légale',
      bio: 'Je m’appelle Hugo. J’ai étudié la psychologie à la Sorbonne, puis suivi une formation en psychologie légale. Je propose une écoute attentive et sans jugement.',
      specialties: ['Écoute', 'Relations', 'Confiance en soi'], nextSlots: ['Samedi 14:00', 'Mardi 19:00'],
      online: true, tone: 'sage', photoUrl: 'portraits/hugo.webp', followed: false,
    },
    {
      id: 'julie', name: 'Julie', initials: 'JU', age: 29, title: 'Accompagnatrice de vie',
      studies: 'Licence en psychologie · Université Paul-Valéry · Spécialisation en psychologie du travail',
      bio: 'Je m’appelle Julie. Après ma licence en psychologie à l’université Paul-Valéry, je me suis spécialisée dans les questions liées au travail. Ici, tu peux parler librement de ce qui te préoccupe.',
      specialties: ['Vie professionnelle', 'Relations', 'Stress du quotidien'], nextSlots: ['Vendredi 16:00', 'Lundi 09:30', 'Mercredi 18:00'],
      online: true, tone: 'peach', photoUrl: 'portraits/julie.webp', followed: false,
    },
    {
      id: 'sarah', name: 'Sarah', initials: 'SA', age: 26, title: 'Accompagnatrice de vie',
      studies: 'Licence en sciences de l’éducation · Université Toulouse Jean-Jaurès · Ingénierie de la formation',
      bio: 'Je m’appelle Sarah. J’ai étudié les sciences de l’éducation à Toulouse Jean-Jaurès et l’accompagnement pédagogique. J’aime aider à retrouver de la clarté dans les périodes de transition.',
      specialties: ['Confiance en soi', 'Transitions', 'Organisation'], nextSlots: ['Samedi 10:30', 'Lundi 17:00', 'Mardi 12:30'],
      online: true, tone: 'lilac', photoUrl: 'portraits/sarah.webp', followed: true,
    },
    {
      id: 'thomas', name: 'Thomas', initials: 'TH', age: 34, title: 'Accompagnateur de vie',
      studies: 'Licence en psychologie · Université de Nîmes · Formation en psychologie clinique',
      bio: 'Je m’appelle Thomas. Après une licence en psychologie à Nîmes, j’ai suivi une formation en psychologie clinique et en accompagnement des personnes. On avance par petites étapes, à ton rythme.',
      specialties: ['Changements de vie', 'Motivation', 'Émotions'], nextSlots: ['Lundi 11:00', 'Jeudi 17:30'],
      online: true, tone: 'blue', photoUrl: 'portraits/thomas.webp', followed: false,
    },
  ];

  posts: Post[] = [
    {
      id: 1, author: 'Lina', initials: 'LI', time: 'Il y a 18 min',
      title: 'J’apprends à dire non, doucement',
      body: 'J’ai réussi à décliner une sortie ce week-end sans inventer d’excuse. Ce n’est pas grand-chose, mais je suis fière de m’être écoutée.',
      topic: 'Confiance en soi', room: 'Tout le monde', likes: 12, replies: 4,
    },
    {
      id: 2, author: 'Maya', initials: 'MA', time: 'Il y a 1 h',
      title: 'Les petits rituels qui font du bien',
      body: 'En ce moment, je note chaque soir une chose que j’ai faite pour moi. Même les jours compliqués, il y en a toujours une.',
      topic: 'Vie quotidienne', room: 'Cercle confiance en soi', likes: 8, replies: 3,
    },
    {
      id: 3, author: 'Camille', initials: 'CA', time: 'Hier',
      title: 'Comment traverser une période de changement ?',
      body: 'Je change de travail le mois prochain et je suis partagée entre impatience et peur. Si vous avez vécu une transition similaire, je vous lis.',
      topic: 'Travail', room: 'Tout le monde', likes: 16, replies: 7,
    },
  ];

  offers: Offer[] = [
    { id: 'community', name: 'Communauté', description: 'Accès à Chat & partage et aux notifications, avec publicités.', price: 0, unit: 'gratuit', active: true },
    { id: 'message', name: 'Une heure par messages', description: 'Un échange individuel écrit, à ton rythme.', price: 13.99, unit: 'la séance', active: true },
    { id: 'video', name: 'Une heure en visio', description: 'Un temps de parole en visioconférence.', price: 14.99, unit: 'la séance', active: true },
    { id: 'chat', name: 'Chat illimité', description: 'Des échanges réguliers par messages avec une accompagnatrice.', price: 24.99, unit: '/ mois', active: true },
    { id: 'four-visio', name: 'Chat + 4 visios', description: 'Chat illimité et quatre visioconférences chaque mois.', price: 33.99, unit: '/ mois', popular: true, active: true },
    { id: 'all-visio', name: 'Chat + visios illimités', description: 'Chat et visioconférences sans limite mensuelle.', price: 49.99, unit: '/ mois', active: true },
  ];

  bookings: Booking[] = [
    { id: 1, coachName: 'Sarah', coachInitials: 'SA', kind: 'Séance par messages · 1 h', dateTime: 'Samedi 17 octobre · 10:30', status: 'Confirmé' },
  ];

  chatThreads = [
    { name: 'Sarah', initials: 'SA', tone: 'lilac', preview: 'On prend le temps, à ton rythme.', time: '10:42', unread: 1, online: true },
    { name: 'Julie', initials: 'JU', tone: 'peach', preview: 'Merci pour ta confiance 🌿', time: 'Hier', unread: 0, online: true },
    { name: 'Cercle confiance', initials: 'CC', tone: 'sage', preview: 'Maya : une petite victoire aujourd’hui', time: 'Mar.', unread: 0, online: false },
  ];

  messages: Record<string, ChatMessage[]> = {
    Sarah: [
      { sender: 'Sarah', text: 'Bonjour Dounia, contente de te retrouver ici. Comment tu te sens aujourd’hui ?', time: '10:32' },
      { sender: 'Dounia', text: 'Un peu fatiguée, mais j’avais envie de parler de cette semaine.', time: '10:39', own: true },
      { sender: 'Sarah', text: 'On prend le temps, à ton rythme. Qu’est-ce qui te ferait du bien de déposer ?', time: '10:42' },
    ],
    Julie: [
      { sender: 'Julie', text: 'Merci pour ta confiance. On pourra reprendre cette question lors de notre prochain échange.', time: 'Hier' },
    ],
    'Cercle confiance': [
      { sender: 'Maya', text: 'J’ai pris dix minutes pour moi avant de commencer la journée.', time: 'Mar.' },
    ],
  };

  get pageTitle(): string {
    const titles: Record<View, string> = {
      home: 'Les Conseils de Doudou', coaches: 'Des personnes à l’écoute', appointments: 'Tes rendez-vous',
      messages: 'Tes conversations', community: 'Un endroit pour partager', profile: 'Ton profil',
      offers: 'Des formules accessibles', companion: 'Ton espace d’accompagnement', admin: 'Espace administration',
    };
    return titles[this.view];
  }

  get filteredCoaches(): Coach[] {
    const q = this.globalQuery.trim().toLocaleLowerCase('fr');
    if (!q) return this.visibleCoaches;
    return this.visibleCoaches.filter((coach) =>
      [coach.name, coach.title, coach.studies, coach.bio, ...coach.specialties].join(' ').toLocaleLowerCase('fr').includes(q),
    );
  }

  get filteredPosts(): Post[] {
    const q = this.communityQuery.trim().toLocaleLowerCase('fr');
    return this.posts.filter((post) => {
      const matchesRoom = !this.isPrivateRoom || post.room !== 'Tout le monde';
      const matchesTopic = this.selectedTopic === 'Tout voir' || post.topic === this.selectedTopic;
      const matchesQuery = !q || [post.title, post.body, post.topic, post.author].join(' ').toLocaleLowerCase('fr').includes(q);
      return matchesRoom && matchesTopic && matchesQuery;
    });
  }

  get activeMessages(): ChatMessage[] {
    return this.messages[this.activeThread] ?? [];
  }

  get followedCount(): number {
    return this.coaches.filter((coach) => coach.followed).length;
  }

  get visibleCoaches(): Coach[] {
    return this.coaches.filter((coach) => coach.online);
  }

  get featuredCoaches(): Coach[] {
    const order = ['hugo', 'julie', 'sarah', 'thomas'];
    const rank = (id: string): number => {
      const index = order.indexOf(id);
      return index === -1 ? order.length : index;
    };
    return [...this.filteredCoaches].sort((a, b) => rank(a.id) - rank(b.id));
  }

  get visibleOffers(): Offer[] {
    return this.offers.filter((offer) => offer.active !== false);
  }

  get activeCoach(): Coach | undefined {
    return this.coaches.find((coach) => coach.name === this.activeThread);
  }

  get companionCoach(): Coach | undefined {
    return this.coaches.find((coach) => coach.id === 'sarah');
  }

  get companionBookings(): Booking[] {
    return this.bookings.filter((booking) => booking.coachName === this.companionCoach?.name);
  }

  ngOnInit(): void {
    this.http.get<Coach[]>('/api/coaches').subscribe({
      next: (data) => { if (data.length) this.coaches = data.map((c) => ({ ...c, tone: this.toneFor(c.id), photoUrl: c.photoUrl || `portraits/${c.id}.webp` })); },
      error: () => undefined,
    });
    this.http.get<Post[]>('/api/posts').subscribe({ next: (data) => { if (data.length) this.posts = data; }, error: () => undefined });
    this.http.get<Offer[]>('/api/offers').subscribe({ next: (data) => { if (data.length) this.offers = data; }, error: () => undefined });
    this.http.get<Booking[]>('/api/bookings').subscribe({ next: (data) => { if (data.length) this.bookings = data; }, error: () => undefined });
    this.http.get<Record<string, ChatMessage[]>>('/api/messages').subscribe({ next: (data) => { if (Object.keys(data).length) this.messages = { ...this.messages, ...data }; }, error: () => undefined });
    this.http.get<typeof this.user>('/api/profile').subscribe({ next: (data) => { if (data?.pseudo) this.user = data; }, error: () => undefined });
  }

  toneFor(id: string): string {
    return ({ sarah: 'lilac', julie: 'peach', hugo: 'sage', thomas: 'blue' } as Record<string, string>)[id] ?? 'lilac';
  }

  go(view: View): void {
    this.view = view;
    this.mobileMenuOpen = false;
    this.profileMenuOpen = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  submitSearch(): void {
    this.go('coaches');
  }

  bookCoach(coach: Coach): void {
    this.selectedCoach = coach;
    this.selectedSlot = coach.nextSlots[0] ?? '';
    this.selectedOffer = 'message';
    this.showBookingModal = true;
  }

  confirmBooking(): void {
    if (!this.selectedCoach || !this.selectedSlot) return;
    const booking: Booking = {
      id: Date.now(), coachName: this.selectedCoach.name, coachInitials: this.selectedCoach.initials,
      kind: this.selectedOffer === 'video' ? 'Séance en visio · 1 h' : 'Séance par messages · 1 h',
      dateTime: this.selectedSlot, status: 'Confirmé',
    };
    this.bookings = [booking, ...this.bookings];
    this.http.post<Booking>('/api/bookings', {
      coach_id: this.selectedCoach.id, offer_id: this.selectedOffer,
      date_time: this.selectedSlot, kind: booking.kind,
    }).subscribe({ next: (saved) => { this.bookings = [saved, ...this.bookings.filter((b) => b.id !== booking.id)]; }, error: () => undefined });
    this.showBookingModal = false;
    this.showToast('Ton rendez-vous est réservé. Tu peux le retrouver ici.');
    this.go('appointments');
  }

  toggleFollow(coach: Coach): void {
    const previous = !!coach.followed;
    coach.followed = !previous;
    this.http.post(`/api/coaches/${coach.id}/follow`, { followed: coach.followed }).subscribe({
      next: () => this.showToast(coach.followed ? `${coach.name} est dans tes suivis.` : `${coach.name} n’est plus dans tes suivis.`),
      error: () => {
        coach.followed = previous;
        this.showToast('Le suivi n’a pas pu être enregistré. Réessaie dans un instant.');
      },
    });
  }

  hidePortrait(event: Event): void {
    (event.target as HTMLImageElement).style.display = 'none';
  }

  toggleLike(post: Post): void {
    post.liked = !post.liked;
    post.likes += post.liked ? 1 : -1;
    this.http.post(`/api/posts/${post.id}/like`, { liked: post.liked }).subscribe({ error: () => undefined });
  }

  addPost(): void {
    const body = this.postDraft.trim();
    if (!body) return;
    const post: Post = {
      id: Date.now(), author: this.user.pseudo, initials: this.user.pseudo.slice(0, 2).toUpperCase(),
      time: 'À l’instant', title: body.length > 72 ? `${body.slice(0, 69)}…` : body,
      body, topic: this.selectedTopic === 'Tout voir' ? 'Vie quotidienne' : this.selectedTopic,
      room: this.isPrivateRoom ? 'Cercle confiance en soi' : 'Tout le monde', likes: 0, replies: 0,
    };
    this.posts = [post, ...this.posts];
    this.http.post<Post>('/api/posts', { ...post, body, is_private: this.isPrivateRoom }).subscribe({
      next: (saved) => { this.posts = [saved, ...this.posts.filter((p) => p.id !== post.id)]; }, error: () => undefined,
    });
    this.postDraft = '';
    this.showPostComposer = false;
    this.showToast('Ton partage a été publié. Merci d’avoir pris la parole.');
  }

  sendMessage(): void {
    const text = this.messageDraft.trim();
    if (!text) return;
    const message: ChatMessage = { sender: this.user.pseudo, text, time: 'À l’instant', own: true };
    this.messages[this.activeThread] = [...this.activeMessages, message];
    this.messageDraft = '';
    this.http.post('/api/messages', { recipient: this.activeThread, text }).subscribe({ error: () => undefined });
  }

  saveProfile(): void {
    this.http.put('/api/profile', this.user).subscribe({ error: () => undefined });
    this.showToast('Ton profil est à jour.');
  }

  addCompanionSlot(): void {
    const slot = this.slotDraft.trim();
    if (!slot || !this.companionCoach || this.companionCoach.nextSlots.includes(slot)) return;
    this.companionCoach.nextSlots.push(slot);
    this.slotDraft = '';
    this.saveCompanionProfile('Le créneau a été ajouté à ton agenda.');
  }

  removeCompanionSlot(slot: string): void {
    if (!this.companionCoach) return;
    this.companionCoach.nextSlots = this.companionCoach.nextSlots.filter((item) => item !== slot);
    this.saveCompanionProfile('Le créneau a été retiré de ton agenda.');
  }

  toggleCompanionAvailability(): void {
    if (!this.companionCoach) return;
    this.companionCoach.online = !this.companionCoach.online;
    this.saveCompanionProfile(this.companionCoach.online ? 'Ton profil est visible dans l’annuaire.' : 'Ton profil est temporairement masqué.');
  }

  saveCompanionProfile(message = 'La présentation de ton profil a été enregistrée.'): void {
    const coach = this.companionCoach;
    if (!coach) return;
    this.http.put('/api/companion/profile', {
      bio: coach.bio, next_slots: coach.nextSlots, active: coach.online,
    }).subscribe({ error: () => undefined });
    this.showToast(message);
  }

  openThread(name: string): void {
    this.activeThread = name;
    if (!this.messages[name]) this.messages[name] = [];
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(price);
  }

  toggleOffer(offer: Offer): void {
    offer.active = !offer.active;
    this.http.patch(`/api/admin/offers/${offer.id}`, { active: offer.active }, { headers: { 'X-Admin-Token': 'demo-admin' } }).subscribe({ error: () => undefined });
    this.showToast(`La formule « ${offer.name} » est ${offer.active ? 'activée' : 'masquée'}.`);
  }

  saveOffer(offer: Offer): void {
    this.http.patch(`/api/admin/offers/${offer.id}`, { price: offer.price }, { headers: { 'X-Admin-Token': 'demo-admin' } }).subscribe({ error: () => undefined });
    this.showToast(`Le tarif de « ${offer.name} » a été mis à jour.`);
  }

  toggleCoach(coach: Coach): void {
    coach.online = !coach.online;
    this.http.patch(`/api/admin/coaches/${coach.id}`, { active: coach.online }, { headers: { 'X-Admin-Token': 'demo-admin' } }).subscribe({ error: () => undefined });
    this.showToast(`${coach.name} est ${coach.online ? 'visible' : 'masqué·e'} dans l’annuaire.`);
  }

  moderate(post: Post): void {
    this.posts = this.posts.filter((item) => item.id !== post.id);
    this.http.delete(`/api/admin/posts/${post.id}`, { headers: { 'X-Admin-Token': 'demo-admin' } }).subscribe({ error: () => undefined });
    this.showToast('Le partage a été retiré de la communauté.');
  }

  showToast(message: string): void {
    this.toast = message;
    if (this.toastTimer) clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => this.toast = '', 3500);
  }
}
