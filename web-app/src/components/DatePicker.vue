<template>
  <div class="date-picker-container">
    <div class="date-picker-wrapper">
      <div class="date-picker-icon">
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>
      <input
        type="date"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :min="minDate"
        :max="maxDate"
        class="date-picker-input"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  minDate: {
    type: String,
    default: null
  },
  maxDate: {
    type: String,
    default: null
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.date-picker-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.date-picker-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  transition: all 0.2s;
}

.date-picker-wrapper:hover {
  border-color: #475569;
  background-color: #334155;
}

.date-picker-wrapper:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.date-picker-icon {
  color: #94a3b8;
  margin-right: 0.75rem;
  pointer-events: none;
}

.date-picker-input {
  background: transparent;
  border: none;
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 500;
  outline: none;
  min-width: 150px;
  cursor: pointer;
}

.date-picker-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  filter: invert(1);
  opacity: 0.6;
}

.date-picker-input::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

/* Style pour le calendrier sur les navigateurs WebKit */
.date-picker-input::-webkit-datetime-edit {
  padding: 0;
}

.date-picker-input::-webkit-datetime-edit-fields-wrapper {
  padding: 0;
}

.date-picker-input::-webkit-datetime-edit-text {
  color: #64748b;
  padding: 0 0.25rem;
}

.date-picker-input::-webkit-datetime-edit-month-field,
.date-picker-input::-webkit-datetime-edit-day-field,
.date-picker-input::-webkit-datetime-edit-year-field {
  color: #f1f5f9;
}

.date-picker-input::-webkit-datetime-edit-month-field:hover,
.date-picker-input::-webkit-datetime-edit-day-field:hover,
.date-picker-input::-webkit-datetime-edit-year-field:hover {
  background-color: rgba(59, 130, 246, 0.2);
  border-radius: 0.25rem;
}

/* Support des thèmes sombres natifs */
@media (prefers-color-scheme: dark) {
  .date-picker-input::-webkit-calendar-picker-indicator {
    filter: invert(1);
  }
}
</style>
