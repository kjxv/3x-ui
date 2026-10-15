package panel

import (
	"testing"

	"github.com/mhsanaei/3x-ui/v3/internal/config"
)

func TestTutorialPresetDisablesUpstreamUpdates(t *testing.T) {
	if !config.IsTutorialPreset() {
		t.Fatal("preset release version is missing")
	}
	service := &PanelService{}
	info, err := service.GetUpdateInfo()
	if err != nil || info.UpdateAvailable || info.CurrentVersion != info.LatestVersion {
		t.Fatalf("unfixed update info: %+v %v", info, err)
	}
	for _, dev := range []bool{false, true} {
		if _, err := service.StartUpdateChannel(dev); err == nil {
			t.Fatal("upstream update was allowed")
		}
	}
}
