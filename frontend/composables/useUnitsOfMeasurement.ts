import { unitsOfMeasurementQuery } from '~/queries/purchases'
import type { UnitOfMeasurement } from '~/types/unitOfMeasurement'

export const useUnitsOfMeasurement = () => {
	const { data: units, status } = useQuery(() => unitsOfMeasurementQuery())

	const unitsBySymbol = computed(() => {
		const map = new Map<string, UnitOfMeasurement>()
		for (const unit of units.value ?? []) {
			map.set(unit.symbol, unit)
		}
		return map
	})

	const unitOptions = computed(() =>
		(units.value ?? []).map((unit) => ({
			label: `${unit.symbol} — ${unit.name}`,
			value: unit.symbol,
		})),
	)

	const getOkeiCode = (symbol: string | undefined | null): string => {
		const key = symbol?.trim()
		if (!key) return ''
		return unitsBySymbol.value.get(key)?.code ?? ''
	}

	return {
		units,
		status,
		unitOptions,
		unitsBySymbol,
		getOkeiCode,
	}
}
