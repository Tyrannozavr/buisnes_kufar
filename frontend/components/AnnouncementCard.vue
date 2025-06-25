<script setup lang="ts">
interface AnnouncementCard {
  id: string
  image: string
  title: string
  date: string
}

defineProps<{
  announcement: AnnouncementCard
}>()

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

const router = useRouter()
const navigateToAnnouncement = (id: string) => {
  router.push(`/announcements/${id}`)
}
</script>

<template>
  <div
    class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer flex px-2"
    @click="navigateToAnnouncement(announcement.id)"
  >
    <div class="w-24 h-24 flex-shrink-0">
      <NuxtImg
        :src="announcement.image"
        :alt="announcement.title"
        class="w-full h-full object-cover rounded-l-lg"
      />
    </div>
    <div class="p-4 flex-1">
      <h2 class="text-lg font-semibold mb-2 line-clamp-2">{{ announcement.title }}</h2>
      <p class="text-sm text-gray-500">{{ formatDate(announcement.date) }}</p>
    </div>
  </div>
</template>