// Developer oracle fixture: algorithm copied from case-7 overtime.go.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

type Punch struct{ InAt, OutAt time.Time }
type Hours struct{ Regular, Overtime float64 }

func weekKey(startUTC time.Time) string {
	y, w := startUTC.ISOWeek()
	return fmt.Sprintf("%d-W%02d", y, w)
}
func WeeklyHours(punches []Punch) map[string]Hours {
	out := map[string]Hours{}
	for _, p := range punches {
		k := weekKey(p.InAt)
		h := out[k]
		h.Regular += p.OutAt.Sub(p.InAt).Hours()
		out[k] = h
	}
	for k, h := range out {
		if h.Regular > 40 {
			h.Overtime = h.Regular - 40
			h.Regular = 40
			out[k] = h
		}
	}
	return out
}
func main() {
	var input map[string][]struct{ In, Out string }
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		panic(err)
	}
	results := map[string]map[string]Hours{}
	for name, rows := range input {
		punches := []Punch{}
		for _, row := range rows {
			in, err := time.Parse(time.RFC3339, row.In)
			if err != nil {
				panic(err)
			}
			out, err := time.Parse(time.RFC3339, row.Out)
			if err != nil {
				panic(err)
			}
			punches = append(punches, Punch{in, out})
		}
		results[name] = WeeklyHours(punches)
	}
	zone, err := time.LoadLocation("America/Chicago")
	if err != nil {
		panic(fmt.Sprintf("required zone data unavailable: %v", err))
	}
	at, _ := time.Parse(time.RFC3339, "2026-09-06T01:00:00Z")
	output := struct {
		ISO           map[string]map[string]Hours `json:"iso"`
		ZoneAvailable bool                        `json:"zone_available"`
		Local         string                      `json:"local"`
	}{results, true, at.In(zone).Format("Mon 2006-01-02 15:04 MST")}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(output); err != nil {
		panic(err)
	}
}
