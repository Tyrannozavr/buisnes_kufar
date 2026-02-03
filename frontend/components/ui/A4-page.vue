<template>
	<div class="a4-background">

		<div class="a4-pages">

			<div class="a4-page_container">
				<div class="a4-page_document">
					<slot />
				</div>
			</div>

		</div>
	</div>
</template>

<script setup lang="ts">

</script>

<style scoped>
.a4-background {
	background-color: #d1d1d1;
	padding: 20px;
	position: relative;
}

.a4-pages {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.a4-page_container {
	height: 297mm;
	width: 210mm;
	background: white;
	margin: 0 auto;
	padding: 10mm;
	box-sizing: border-box;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	overflow: hidden;
}

.a4-page_document {
	font-size: 14px;
	font-family: serif;
}

</style>