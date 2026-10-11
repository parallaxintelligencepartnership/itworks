package main
import("fmt";"time")
type Punch struct {InAt,OutAt time.Time}
type Hours struct {Regular,Overtime float64}
func weekKey(startUTC time.Time) string {y,w:=startUTC.ISOWeek();return fmt.Sprintf("%d-W%02d",y,w)}
func WeeklyHours(punches []Punch) map[string]Hours {out:=map[string]Hours{};for _,p:=range punches{k:=weekKey(p.InAt);h:=out[k];h.Regular+=p.OutAt.Sub(p.InAt).Hours();out[k]=h};for k,h:=range out{if h.Regular>40{h.Overtime=h.Regular-40;h.Regular=40;out[k]=h}};return out}
func main(){var punches []Punch;for _,s:=range []string{"2026-08-31T13:00:00Z","2026-09-01T13:00:00Z","2026-09-02T13:00:00Z","2026-09-03T13:00:00Z","2026-09-04T13:00:00Z","2026-09-06T01:00:00Z"}{t,_:=time.Parse(time.RFC3339,s);punches=append(punches,Punch{t,t.Add(8*time.Hour)});fmt.Println(s,weekKey(t))};fmt.Printf("WeeklyHours=%+v\n",WeeklyHours(punches))}
