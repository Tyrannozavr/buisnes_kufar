<script setup lang="ts">
const showConsent = ref(false);
const cookieConsent = useCookie('cookie_consent');

// Проверяем, дал ли пользователь согласие
onMounted(() => {
  if (!cookieConsent.value) {
    showConsent.value = true;
  }
});

// Принимаем куки и скрываем уведомление
const acceptCookies = () => {
  cookieConsent.value = 'accepted';
  showConsent.value = false;
};
</script>
<template>
  <UModal
      v-model:open="showConsent"
      title="Согласие на использование cookies"
      >
    <template #body>
      Мы используем cookies для авторизации и улучшения работы сайта. Продолжая использовать сайт, вы соглашаетесь с этим.
    </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton
            color="primary"
            @click="acceptCookies"
          >
            Принять
          </UButton>
        </div>
      </template>
  </UModal>

</template>